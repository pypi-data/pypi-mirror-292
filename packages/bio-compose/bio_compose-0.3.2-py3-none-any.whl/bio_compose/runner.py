# Runner for interacting with the "execute-simulations" group of endpoints
import os 
import abc
from typing import * 

from requests_toolbelt.multipart.encoder import MultipartEncoder

from bio_compose.data_model import Api


class SimulationRunner(Api):
    endpoint_root: str
    data: Dict
    submitted_jobs: List[Dict]

    def __init__(self):
        """A new instance of the Verifier class. NOTE: this may clash with your record keeping in a notebook, so it is highly recommended that users
            treat instances of this class as quasi-singletons, although not necessary for fundamental interaction.
        """
        super().__init__()

    def run_smoldyn_simulation(self, smoldyn_configuration_filepath: str, duration: int = None, dt: float = None):
        endpoint = self._format_endpoint(f'run-smoldyn')
        
        # multipart
        input_fp = (smoldyn_configuration_filepath.split('/')[-1], open(smoldyn_configuration_filepath, 'rb'), 'application/octet-stream')
        encoder_fields = {'uploaded_file': input_fp}
        multidata = MultipartEncoder(fields=encoder_fields)

        # query and headers
        query_params = {}
        query_args = [('duration', duration), ('dt', dt)]
        for arg in query_args:
            if arg[1] is not None:
                query_params[arg[0]] = str(arg[1])

        headers = {'Content-Type': multidata.content_type}

        return self._execute_request(endpoint=endpoint, headers=headers, multidata=multidata, query_params=query_params)
        
    def run_utc_simulation(self, sbml_filepath: str, start: int, end: int, steps: int, simulator: str):
        endpoint = self._format_endpoint(f'run-utc')

        # multipart 
        input_fp = (sbml_filepath.split('/')[-1], open(sbml_filepath, 'rb'), 'application/octet-stream')
        encoder_fields = {'uploaded_file': input_fp}
        multidata = MultipartEncoder(fields=encoder_fields)

        # query and headers
        query_params = {
            'start': str(start), 
            'end': str(end),
            'steps': str(steps),
            'simulator': simulator
        }
        headers = {'Content-Type': multidata.content_type}

        return self._execute_request(endpoint=endpoint, headers=headers, multidata=multidata, query_params=query_params)
    
    def generate_simularium_file(self, smoldyn_output_filepath: str, box_size: float, filename: str = None):
        endpoint = self._format_endpoint(f'generate-simularium-file')

        # multipart 
        input_fp = (smoldyn_output_filepath.split('/')[-1], open(smoldyn_output_filepath, 'rb'), 'application/octet-stream')
        encoder_fields = {'uploaded_file': input_fp}
        multidata = MultipartEncoder(fields=encoder_fields)

        # query
        query_params = {'box_size': str(box_size)}
        if filename is not None:
            query_params['filename'] = filename

        # headers 
        headers = {'Content-Type': multidata.content_type}

        return self._execute_request(endpoint=endpoint, headers=headers, multidata=multidata, query_params=query_params)
        
        
    
        