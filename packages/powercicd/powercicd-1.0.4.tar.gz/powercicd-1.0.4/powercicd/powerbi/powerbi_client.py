# %%
import copy
import gzip
import json
import logging
import mimetypes
import os
import re
import time
import urllib
from pathlib import Path
from typing import Any
from urllib.parse import quote
from urllib.request import Request, urlopen

import azure.identity._credentials.browser as azure_browser
import requests
from azure.core.credentials import AccessToken
from azure.identity import DefaultAzureCredential
from requests.sessions import Session
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chromium.webdriver import ChromiumDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from tenacity import retry, stop_after_attempt, wait_fixed

from powercicd.powerbi.config import DatasetRefreshSchedule, Report, Group, Datasource
from powercicd.shared.logging_utils import log_call
from powercicd.shared.selenium_common import new_browser

# %%
log = logging.getLogger(__name__)


# TODO: Migrate whole retrieve and deploy scripts to python by using example: https://github.com/Azure-Samples/powerbi-powershell/blob/master/manageRefresh.ps1

retry_6times_10sec = retry(stop=stop_after_attempt(6), wait=wait_fixed(10), reraise=True, before_sleep=lambda _: log.info("Call failed, Retrying..."))


def build_datasource_key(ds) -> str:
    return "_".join([ds[key].strip(" /") for key in sorted(ds) if isinstance(ds[key], str)])


class PowerBiWebClient:
    def __init__(self, tenant: str, keep_browser_open: bool):
        self.keep_browser_open              : bool = keep_browser_open
        self.tenant                         : str  = tenant
        self.import_timeout_seconds         : int  = 60 * 60 * 30
        self.import_polling_seconds         : int  = 60
        self.active_refresh_timeout_seconds : int  = 60 * 60 * 20
        self.active_refresh_polling_seconds : int  = 60
        self.powerbi_url                    : str  = f"https://app.powerbi.com/home?ctid={quote(self.tenant)}&experience=power-bi"
        
        # defining the azure credential for REST API
        az_credential_for_rest_api_default_args = {
            "exclude_workload_identity_credential"   : True,
            "exclude_developer_cli_credential"       : True,
            "exclude_cli_credential"                 : True,
            "exclude_environment_credential"         : True,
            "exclude_managed_identity_credential"    : True,
            "exclude_powershell_credential"          : True,
            "exclude_visual_studio_code_credential"  : True,
            "exclude_shared_token_cache_credential"  : True,
            "exclude_interactive_browser_credential" : False,
            "interactive_browser_tenant_id"          : tenant,
        }
        az_credential_for_rest_api_default_env_args = {
            k.lower().replace("az_credential_", ""): v
            for k, v in os.environ.items()
            if k.lower().startswith("az_credential_")
        }
        args = {**az_credential_for_rest_api_default_args, **az_credential_for_rest_api_default_env_args}        
        log.info(f"Creating Azure credential for REST API with args: {args}")
        self.az_credential_for_rest_api  : DefaultAzureCredential = DefaultAzureCredential(**args)        
        self._browser                       : None | ChromiumDriver  = None
        self._token                         : None | AccessToken     = None
        self._session                       : None | Session         = None

    @property 
    def browser(self) -> ChromiumDriver:
        if self._browser is None:
            self._browser = new_browser(self.tenant, self.keep_browser_open)
        return self._browser

    def close_browser(self):
        if self.keep_browser_open:
            return
            
        if self._browser is not None:
            log.info("Closing the browser...")
            self._browser.quit()
            self._browser = None
        else:
            log.info("No browser to close.")
        
    @property
    def wait_browser(self) -> WebDriverWait:
        return WebDriverWait(self.browser, 10)

    def _has_token_expired(self):
        return self._token is None or self._token.expires_on < time.time() + 60

    @property
    def token_string(self):
        if self._has_token_expired():
            # noinspection PyProtectedMember
            az_open_browser_fn = azure_browser._open_browser
            try:
                # replace the open browser function to use the current browser instead of opening a new one
                azure_browser._open_browser = lambda url: self.browser.get(url) is None
                self._token: AccessToken = self.az_credential_for_rest_api.get_token("https://analysis.windows.net/powerbi/api/.default")
            finally:
                azure_browser._open_browser = az_open_browser_fn
                
        return self._token.token

    @property
    def session(self):
        # if self._session is None or self._has_token_expired():
        self._session = requests.Session()
        self._session.headers.update({
            "Authorization": f"Bearer {self.token_string}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        })            
        return self._session

    def get_json_and_extract_value(self, url: str, *path_to_extract, _timeout=10) -> Any:
        r = self.session.get(url)
        if r.status_code // 100 != 2:
            raise ValueError(f"GET '{url}': Failed with status code '{r.status_code}' and response: {r.text}")
        try:
            r_json = r.json()
        except:
            log.exception(f"GET '{url}': Failed to parse json of response: {r.text}")
            raise

        # reach the desired object
        obj = r_json
        current_path = []
        for p in path_to_extract:
            current_path.append(p)
            if not isinstance(obj, (dict, list)):
                raise ValueError(f"GET '{url}': Expected a dict or list at path '{current_path}', but got '{obj}'")
            if p not in obj:
                raise ValueError(f"GET '{url}': Expected key '{p}' at path '{current_path}', but available keys are '{list(obj.keys())}' in '{obj}'")
            obj = obj[p]
            
        return obj 


    def login_for_powerbi_api(self):
        dummy = self.token_string
        log.info("Logged in to Power BI API")

    def is_logged_in_for_selenium(self):
        log.info("Verifying login for selenium")

        log.info(f"Opening the Power BI tenant site: '{self.powerbi_url}'")
        self.browser.get(self.powerbi_url)
        
        log.info("Analyzing the page...")
        try:
            _ = self.wait_browser.until(EC.element_to_be_clickable((By.CLASS_NAME, "userInfoButton")))
            log.info("Logged in!")
            return True
        except TimeoutException:
            log.info("Not logged in.")
            return False
        
    def login_for_selenium(self):
        if self.is_logged_in_for_selenium():
            return

        print("-------------------------------------------------------------------------------")
        input("Please login manually in the opened browser window and press Enter to continue.")
        
        if not self.is_logged_in_for_selenium():
            raise ValueError("Login check failed even after manual login. Please check the opened browser window.")

    @log_call()
    def try_get_group_by_name(self, group_name: str) -> Group | None:
        groups: list[Group] = self.get_json_and_extract_value("https://api.powerbi.com/v1.0/myorg/groups", 'value')
        groups = [g for g in groups if g['name'] == group_name]
        if len(groups) == 0:
            return None
        elif len(groups) > 1:
            raise ValueError(f"Multiple powerbi groups/workspaces with the same name '{group_name}' found... You must delete the duplicates.")
        return groups[0]

    def get_group_by_name(self, group_name: str) -> Group:
        group = self.try_get_group_by_name(group_name)
        if group is None:
            raise ValueError(f"Group '{group_name}' not found")
        return group

    @log_call()
    def try_get_report_by_name(self, group_id: str, report_name: str) -> Report | None:
        reports: list[Report] = self.get_json_and_extract_value(f"https://api.powerbi.com/v1.0/myorg/groups/{group_id}/reports", 'value')
        reports = [ri for ri in reports if ri['name'] == report_name]
        if len(reports) == 0:
            return None
        elif len(reports) > 1:
            raise ValueError(f"Multiple reports with the same name '{report_name}' found in group '{group_id}'... You must delete the duplicates.")
        return reports[0]

    @log_call()
    @retry_6times_10sec
    def get_report_by_name(self, group_id: str, report_name: str) -> Report:
        reports: list[Report] = self.get_json_and_extract_value(f"https://api.powerbi.com/v1.0/myorg/groups/{group_id}/reports", 'value')
        reports = [ri for ri in reports if ri['name'] == report_name]
        if len(reports) == 0:
            raise ValueError(f"Report '{report_name}' not found in group '{group_id}'")
        elif len(reports) > 1:
            raise ValueError(f"Multiple reports with the same name '{report_name}' found in group '{group_id}'... You must delete the duplicates.")
        return reports[0]

    @log_call()
    @retry_6times_10sec
    def get_report_by_id(self, group_id: str, report_id: str) -> Report:
        return self.get_json_and_extract_value(f"https://api.powerbi.com/v1.0/myorg/groups/{group_id}/reports/{report_id}", 'value')

    @log_call()
    @retry_6times_10sec
    def get_import_by_id(self, group_id: str, import_id: str) -> Report:
        return self.get_json_and_extract_value(f"https://api.powerbi.com/v1.0/myorg/groups/{group_id}/imports/{import_id}")

    @log_call()
    def wait_until_import_is_succeeded(self, group_id: str, import_id: str):
        start_monotonic = time.monotonic()
        while True:
            if time.monotonic() - start_monotonic > self.import_timeout_seconds:
                raise TimeoutError("Waiting for the end of the import took too long.")
            importt = self.get_import_by_id(group_id, import_id)
            # remark: see doc at: https://learn.microsoft.com/en-us/rest/api/power-bi/imports/get-imports-in-group#import
            if importt['importState'] == "Succeeded":
                log.info("Import succeeded.")
                return importt
            if importt['importState'] == "Failed":
                raise ValueError(f"Import failed: {importt['error']['message']}")
            log.info(f"Import in progress... sleep {self.import_polling_seconds} seconds")
            time.sleep(self.import_polling_seconds)

    @log_call()
    @retry_6times_10sec
    def wait_for_end_of_any_active_dataset_refresh(self, group_id: str, dataset_id: str):
        start_monotonic = time.monotonic()
        while True:
            if time.monotonic() - start_monotonic > self.active_refresh_timeout_seconds:
                raise TimeoutError("Waiting for the end of any active dataset refresh took too long.")

            refreshes = self.get_json_and_extract_value(f"https://api.powerbi.com/v1.0/myorg/groups/{group_id}/datasets/{dataset_id}/refreshes", 'value')
            refreshes_in_status_unknown = [r for r in refreshes if r["status"] == "Unknown"]
            if len(refreshes_in_status_unknown) == 0:
                log.info("No active refreshes.")
                break
            log.info(f"{len(refreshes_in_status_unknown)} Active refreshes... sleep {self.active_refresh_polling_seconds} seconds")
            time.sleep(self.active_refresh_polling_seconds)

    @log_call()
    @retry_6times_10sec
    def get_dataset(self, group_id, dataset_id):
        return self.get_json_and_extract_value(f"https://api.powerbi.com/v1.0/myorg/groups/{group_id}/datasets/{dataset_id}")  # Remark: weird API: no value key here!!!!
        
    @log_call()
    def retrieve_report(self, group_id: str, report_id: str, pbix_filepath: str):
        log.info(f"Downloading the report: '{report_id}' to '{pbix_filepath}'")
        file_dir  = Path(pbix_filepath).parent
        file_dir.mkdir(parents=True, exist_ok=True)
        
        url = f"https://api.powerbi.com/v1.0/myorg/groups/{group_id}/reports/{report_id}/Export"
        request = Request(url, method="GET", headers=self.session.headers)
        with (
            urlopen(request) as response,
            gzip.GzipFile(fileobj=response, mode='rb') as uncompressed,
            open(pbix_filepath, "wb") as out_file
        ):
            while True:
                chunk = uncompressed.read(1024 * 1024)
                if not chunk:
                    break
                log.info(f"Writing {len(chunk)} bytes to '{pbix_filepath}'")
                out_file.write(chunk)

    @log_call()
    @retry_6times_10sec
    def ensure_dataset_ownership(self, group_id: str, dataset_id: str):
        dataset = self.get_dataset(group_id, dataset_id)
        if self.az_credential_for_rest_api.credentials[0]._auth_record.username == dataset['configuredBy']:
            log.info(f"Dataset '{dataset_id}' is already owned by the current user.")
            return

        log.info(f"Taking over the dataset: '{dataset_id}'")
        url = f"https://api.powerbi.com/v1.0/myorg/groups/{group_id}/datasets/{dataset_id}/Default.TakeOver"
        self.session.post(url)

    @log_call()
    @retry_6times_10sec
    def update_dataset_parameters(self, group_id: str, dataset_id: str, dataset_parameters: dict[str, str]):
        body = {
            "updateDetails": [
                {
                    "name": key,
                    "newValue": value
                }
                for key, value
                in dataset_parameters.items()
            ]
        }
        url = f"https://api.powerbi.com/v1.0/myorg/groups/{group_id}/datasets/{dataset_id}/Default.UpdateParameters"
        self.session.post(url, json=body)

    @log_call()
    def import_report(
        self,
        group_id: str,
        report_name: str,
        file_path: str,
    ) -> str:
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        content_type, _ = mimetypes.guess_type(file_path)
        boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
        part1 = (
            f'--{boundary}\r\n'
            f'Content-Disposition: form-data; name="value"; filename="{file_name}"\r\n'
            f'Content-Type: {content_type}\r\n\r\n'
        ).encode()        
        part2 = f'\r\n--{boundary}--\r\n'.encode()
        total_size = len(part1) + file_size + len(part2)

        headers = copy.copy(self.session.headers)
        headers["Content-Type"] = f'multipart/form-data; boundary={boundary}'
        headers["User-agent"] = "PostmanRuntime/7.40.0"
        headers["Connection"] = "keep-alive"
        headers["Accept"] = "application/json"
        headers["Accept-Encoding"] = "gzip, deflate, br"
        headers["Cache-Control"] = "no-cache"
        headers["Content-Length"] = str(total_size)
                
        def generate_body():
            yield part1
            with open(file_path, 'rb') as f:
                while True:
                    chunk = f.read(1024 * 1024)
                    if not chunk:
                        break
                    yield chunk
            yield part2

        # rest service expects the pbix extension
        report_name_with_file_extension = report_name + ".pbix"
        url = f"https://api.powerbi.com/v1.0/myorg/groups/{group_id}/imports?datasetDisplayName={quote(report_name_with_file_extension)}&nameConflict=CreateOrOverwrite"

        req = Request(url, method="POST", headers=headers, data=generate_body())
        try:
            with urlopen(req) as r:
                 r_binary = r.read1()
        except urllib.error.HTTPError as e:
            request_response = e.read().decode()
            msg = f"Failed to import the report '{report_name}' from '{file_path}', POST {req.full_url=} with headers: {req.headers}, response: {request_response}"
            raise ValueError(msg) from e
        except Exception as e:
            msg = f"Failed to import the report '{report_name}' from '{file_path}', POST {req.full_url=} with headers: {req.headers}"
            raise ValueError(msg) from e

        try:
            r_text = gzip.decompress(r_binary).decode() if r.info().get('Content-Encoding') == 'gzip' else r_binary.decode()
        except:
            log.exception(f"Failed to parse the response of the import request: {r_binary}")
            raise

        if r.status // 100 != 2:
            raise ValueError(f"Failed to import: status={r.status}, body='{r_text}'")
        
        try:
            r_json = json.loads(r_text)
        except:
            log.exception(f"Failed to parse the json of the response: {r_text}")
            raise

        try:
            import_id = r_json['id']
        except:
            log.exception(f"Failed to extract the (report) id from the response: {r_json}")
            raise
        
        return import_id

    @log_call()
    @retry_6times_10sec
    def get_gateway_cluster_datasources(self, gateway_type: str | None = None) -> list[Datasource]:
        all_datasources = self.get_json_and_extract_value("https://api.powerbi.com/v2.0/myorg/me/gatewayClusterDatasources?$expand=users", 'value')
        if gateway_type is None:
            return all_datasources
        else:
            return [s for s in all_datasources if s['gatewayType'] == gateway_type]

    @log_call()
    @retry_6times_10sec
    def get_dataset_datasources(self, group_id: str, dataset_id: str) -> list[Datasource]:
        return self.get_json_and_extract_value(f"https://api.powerbi.com/v1.0/myorg/groups/{group_id}/datasets/{dataset_id}/datasources", 'value')

    @log_call()
    def bind_dataset_to_gateway(self, group_id: str, dataset_id: str, gateway_id: str, datasource_ids: list[str]):
        body = {
            "gatewayObjectId": gateway_id,
            "datasourceObjectIds": datasource_ids
        }
        url = f"https://api.powerbi.com/v1.0/myorg/groups/{group_id}/datasets/{dataset_id}/Default.BindToGateway"
        self.session.post(url, json=body)

    @log_call()
    @retry_6times_10sec
    def set_dataset_refresh_schedule(self, group_id: str, dataset_id: str, refresh_schedule: DatasetRefreshSchedule):
        body = {
            "value": refresh_schedule.model_dump()
        }
        url = f"https://api.powerbi.com/v1.0/myorg/groups/{group_id}/datasets/{dataset_id}/refreshSchedule"
        self.session.patch(url, json=body)

    @log_call()
    @retry_6times_10sec
    def update_report_content(self, group_id: str, upload_report_id: str, final_report_id: str):
        body = {
            "sourceReport": {
                "sourceReportId" : upload_report_id,
                "sourceWorkspaceId" : group_id,
            },
            "sourceType": "ExistingReport",
        }

        url = f"https://api.powerbi.com/v1.0/myorg/groups/{group_id}/reports/{final_report_id}/Default.UpdateContent"
        self.session.post(url, json=body)

    @log_call()
    @retry_6times_10sec
    def rebind_report_to_dataset(self, group_id: str, report_id: str, dataset_id: str):
        body = {
            "datasetId": dataset_id
        }
        url = f"https://api.powerbi.com/v1.0/myorg/groups/{group_id}/reports/{report_id}/Rebind"
        self.session.post(url, json=body)

    @log_call()
    @retry_6times_10sec
    def clone_report(self, group_id: str, report_id: str, final_report_name: str):
        body = {
            "name": final_report_name
        }
        url = f"https://api.powerbi.com/v1.0/myorg/groups/{group_id}/reports/{report_id}/Clone"
        self.session.post(url, json=body)

    @log_call()
    def deploy_app(self, group_id: str, log_dir: str):
        try:
            # %%
            group_url = f"https://app.powerbi.com/groups/{group_id}/list?ctid={quote(self.tenant)}&experience=power-bi"
            log.info(f"Opening the group: '{group_url}'")
            self.browser.get(group_url)

            # %%
            log.info("Waiting for the update app button in group view to appear...")
            update_button = self.wait_browser.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='update-app']")))
            update_button.click()

            # %%
            log.info("Waiting for the update app button in update dialog to appear...")
            update_app_publish_button = self.wait_browser.until(EC.presence_of_element_located((By.CSS_SELECTOR, "button[data-testid='update-app-publish']")))
            # check if the button is enabled
            if not update_app_publish_button.is_enabled():
                screenshot_path = f"{log_dir}/disabled_update_screenshot.png"
                self.browser.save_screenshot(screenshot_path)
                log.warning(
                    f"The 'Update app' button is disabled. You need to deploy manually to (re-)configure the app!" 
                    f"\n  --> URL '{self.browser.current_url}'. \n --> Screenshot saved to '{screenshot_path}'"
                )
                return
            log.info("Publishing the app... ('Update app' button is enabled)")
            update_app_publish_button.click()

            # %%
            ok_button = self.wait_browser.until(EC.element_to_be_clickable((By.ID, "okButton")))
            ok_button.click()

            # %%
            input_publish_url = self.wait_browser.until(EC.presence_of_element_located((By.ID, "app-publish-url")))
            publish_url = input_publish_url.get_attribute("value")
            log.info(f"!!!! Published app URL: {publish_url}")
        except:
            screenshot_path = f"{log_dir}/error_screenshot.png"
            self.browser.save_screenshot(screenshot_path)
            log.exception(f"Failed to deploy the app. Screenshot saved to '{screenshot_path}'")
            raise

    @log_call()
    @retry_6times_10sec
    def cleanup_reports(self, group_id: str, cleanup_regex: str, exclude_report_names: list[str]):
        exclude_report_names = set(exclude_report_names)

        re_cleanup = re.compile(cleanup_regex)

        reports_url = f"https://api.powerbi.com/v1.0/myorg/groups/{group_id}/reports"
        datasets_url = f"https://api.powerbi.com/v1.0/myorg/groups/{group_id}/datasets"
        
        reports = self.get_json_and_extract_value(reports_url, 'value')
        
        reports_to_delete = [r for r in reports if re_cleanup.match(r['name']) and r['name'] not in exclude_report_names]
        for report in reports_to_delete:
            report_id = report['Id']
            try:
                log.info(f"Deleting report '{report['name']}' with id '{report_id}'")
                report_url = f"https://api.powerbi.com/v1.0/myorg/groups/{group_id}/reports/{report_id}"
                self.session.delete(report_url)
                log.info(f"Report deleted successfully.")
            except:
                log.exception(f"Failed to delete report '{report['name']}'")

        reports = self.get_json_and_extract_value(reports_url, 'value')
        
        reports_dataset_ids = set(r['datasetId'] for r in reports)
        datasets = self.get_json_and_extract_value(datasets_url, 'value')

        datasets_to_delete = [d for d in datasets if d['id'] not in reports_dataset_ids]
        for dataset in datasets_to_delete:
            dataset_id = dataset['id']
            try:
                log.info(f"Deleting dataset '{dataset['name']}' with id '{dataset_id}'")
                dataset_url = f"https://api.powerbi.com/v1.0/myorg/groups/{group_id}/datasets/{dataset_id}"
                self.session.delete(datasets_url)
                log.info(f"Dataset deleted successfully.")
            except:
                log.exception(f"Failed to delete dataset '{dataset['name']}'")

    @log_call()
    def deploy_report(
        self,
        group_id: str,
        upload_report_name: str,
        final_report_name: str,
        pbix_file_path: str,
        dataset_parameters: dict[str, str] = None,
        refresh_schedule: DatasetRefreshSchedule | None = None,
        cleanup_regex: str | None = None,
    ):
        report_before = self.try_get_report_by_name(group_id, upload_report_name)

        if report_before is not None:
            log.warning(f"Report '{upload_report_name}' already exists in the group '{group_id}'. Report and underlying semantic model may be temporarily out-of-sync!!")
            self.ensure_dataset_ownership(group_id, report_before['datasetId'])

        # UPLOAD PBIX FILE!
        import_id    = self.import_report(group_id, upload_report_name, pbix_file_path)
        importt      = self.wait_until_import_is_succeeded(group_id, import_id)
        report_id    = importt['reports' ][0]['id']
        dataset_id   = importt['datasets'][0]['id']

        self.ensure_dataset_ownership(group_id, dataset_id)
        self.wait_for_end_of_any_active_dataset_refresh(group_id, dataset_id)
        if dataset_parameters is not None:
            self.update_dataset_parameters(group_id, dataset_id, dataset_parameters)

        # identify managed datasources to bind to the gateway cluster datasources
        tenant_datasources               = self.get_gateway_cluster_datasources("TenantCloud")
        dataset_datasources              = self.get_dataset_datasources(group_id, dataset_id)
        tenant_datasources_by_key        = { build_datasource_key(ds) : ds for ds in tenant_datasources }
        datasources_by_key               = { build_datasource_key(ds) : ds for ds in dataset_datasources }
        unmanaged_datasource_keys        = sorted(set(datasources_by_key.keys()) - set(tenant_datasources_by_key.keys()))
        managed_datasource_keys          = sorted(set(datasources_by_key.keys()) & set(tenant_datasources_by_key.keys()))
        managed_datasource_by_gateway_id = {
            tenant_datasources_by_key[key]['clusterId'] : tenant_datasources_by_key[key]
            for key
            in managed_datasource_keys
        }
        log.info(f"{unmanaged_datasource_keys=}, {managed_datasource_keys=}")

        # bind datasource to relevant gateway datasources
        for gateway_id, dataset_datasources in managed_datasource_by_gateway_id.items():
            tenant_datasource_ids = [ds['id'] for ds in dataset_datasources]
            self.bind_dataset_to_gateway(group_id, dataset_id, gateway_id, tenant_datasource_ids)

        # trigger dataset refresh
        self.wait_for_end_of_any_active_dataset_refresh(group_id, dataset_id)
        url = f"https://api.powerbi.com/v1.0/myorg/groups/{group_id}/datasets/{dataset_id}/refreshes"
        self.session.post(url)
        self.wait_for_end_of_any_active_dataset_refresh(group_id, dataset_id)

        # set refresh schedule
        if refresh_schedule is not None:
            self.set_dataset_refresh_schedule(group_id, dataset_id, refresh_schedule)

        # finalize the report
        final_report = self.try_get_report_by_name(group_id, final_report_name)
        if final_report is not None:
            final_report_id = final_report['id']
            final_report_dataset_id = final_report['datasetId']
            self.ensure_dataset_ownership(group_id, final_report_dataset_id)
            self.wait_for_end_of_any_active_dataset_refresh(group_id, final_report_dataset_id)
            self.update_report_content(group_id, final_report_id, report_id)
            self.rebind_report_to_dataset(group_id, final_report_id, dataset_id)
        else:
            self.clone_report(group_id, report_id, final_report_name)
            final_report = self.try_get_report_by_name(group_id, final_report_name)
            final_report_id = final_report['id']
            final_report_dataset_id = final_report['datasetId']

        # cleanup
        if cleanup_regex is not None:
            self.cleanup_reports(group_id, cleanup_regex, exclude_report_names=[final_report_name])
