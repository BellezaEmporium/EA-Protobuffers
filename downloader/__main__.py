from remote_zip import RemoteZip
import requests
import os
import shutil
import logging
import zlib

# logging.basicConfig(level=logging.DEBUG)

WHITELISTED_EXES = [exe.lower() for exe in ["EABackgroundService", "EAConnect_microsoft", "EADesktop", "EAEgsProxy", "EAGEP", "EALaunchHelper", "EALocalHostSvc", "EASteamProxy", "EAUpdater", "Link2EA"]]

AUTOPATCH_BUCKET = 'https://autopatch.juno.ea.com/autopatch/upgrade/buckets/999'

def version_url(version: str) -> str:
    return f'https://autopatch.juno.ea.com/autopatch/versions/{version}?locale=en_US'


session = requests.Session()

session.headers['User-Agent'] = 'EADownloader'

bucket_response = session.get(AUTOPATCH_BUCKET)
bucket = bucket_response.json()

recommended_version = bucket['recommended']['version']

version_response = session.get(version_url(recommended_version))
version_manifest = version_response.json()

shutil.rmtree('temp', ignore_errors=True)
os.makedirs('temp')

url = version_manifest['downloadURL']

zip = RemoteZip(url, session)

zip.setup()

for file in zip.central_directory.files:
    file_name = os.path.basename(file.file_name)
    if ".exe" in file.file_name and len(file.file_name.split('/')) == 2 and file_name.split('.')[0].lower() in WHITELISTED_EXES:
        file_data = zip.get_bytes_from_file(file.file_data_offset, file.compressed_size)
        assert file.compression_method == 8
        decompressor = zlib.decompressobj(-15)
        with open(f'temp/{file_name}', 'wb') as f:
            f.write(decompressor.decompress(file_data))

