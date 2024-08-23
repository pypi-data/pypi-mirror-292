from openi import OpenIApi

api = OpenIApi(
    token="51038a291e51fb7780df7f6b86661d26fc3a3457",
    endpoint="http://192.168.207.34",
)

info = api.query_dataset_file(
    repo_id="wjtest0421-2/proA",
    filename="2022-04-21wjtest_MnistData.zip",
    upload_type=0,
)

print(info)
