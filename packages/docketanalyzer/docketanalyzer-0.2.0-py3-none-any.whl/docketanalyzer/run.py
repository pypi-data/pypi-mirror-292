from docketanalyzer import load_docket_index


docket_id = "azd__2_17-cv-02434"

index = load_docket_index()
manager = index[docket_id]
table = index.table
data = table.pandas()
print(data)
print(data['task_parse_dockets'].isnull().mean())