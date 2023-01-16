My personal database solution for managing other projects and viewing related data.

Requires linux and python >= 3.10. The database is MongoDB.

---

To get all set up, first download the repo, then install dependencies:
```bash
git clone https://github.com/ZacharyWesterman/server.git --recursive
cd server
poetry install
```

You will want to make sure you have a place to store blob data that is uploaded to the site.
It can be any directory, but going forward we'll assume it's `/var/blob_data`.

Also, make sure you know the MongoDB URLs of the various databases involved. If not specified at run-time, these will all default to `localhost`.

Currently there are two databases, one for weather users (see my [weather-alerts repo](https://github.com/ZacharyWesterman/weather-alerts) ), and one for all other data.

---

To run this application with minimal params:
```bash
./run.sh --blob-path=/var/blob_data
```

Additional parameters are available. You can run `./run.sh --help` to see them all.
