# Pylegiscan
### This project gives a number of helper functions
- get_legiscan_json(legiscan_key, access_key, out_dir): uses the legiscan api to get the bulk data
- get_people(people_dir): parses the people data
- get_bills(bill_dir): parses the bill data
- get_votes(vote_dir): parses the vote data
- convert_pylegiscan_json(people_dir, bill_dir, vote_dir, out_dir): combines all the parsing and outputs them into parquet files