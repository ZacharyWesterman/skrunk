My home-built database solution for managing personal data and interacting with other projects.

Current features include:
- Full support for modern Android/iOS mobile as well as desktop browsers.
- A fully featured library/book cataloging system: type the name of a book, click the correct match, then scan a QR code, barcode, or RFID tag. Bam, it's now cataloged under your name, and you can easily find it later, specify if someone's borrowing it, transfer ownership, etc.
- File storage with advanced tagging functionality and minimal limitations. Want to upload 75 photos of your dog? Can do, just select them all and add the "dog" and "my-dog's-name" tags when uploading. Has it been 10 years and you can't find those images? Just search for your dog's name. Want to download all the results from that search? Just click the "download all" button. Don't want anyone else to see that video of you in a tutu? Just mark the file as "only visible to me".
- Allow users to report bugs, request new features, and see what features are planned or in progress.
- [Weather Alerts](https://github.com/ZacharyWesterman/weather-alerts) integration: if you moved, changed your phone number, want to change the default temperature thresholds, or just disable your alerts altogether, you can do so in the user settings page.
- Subsonic Music Server Integration: Search albums, and interact with the Library to show what books also have an audiobook version.
- Dynamic theme: If you don't like the default colors or styling, you can always change it in user settings.
- Fine-grained user control:
  - User Isolation: Sometimes you don't want certain groups of users to interact (e.g. in-laws, different friend groups, etc). If that's the case, admins can assign a "group" to users. Any users not in the same group will not be able to see or interact with each other's data.
  - User Permissions: Control what type of actions users are allowed to do, and what they're allowed to see.

Every one of the above features is fully optional, and can be enabled or disabled from the admin options.

---
### Setup

This application requires some flavor of Linux (tested on Ubuntu 22), Python &ge; 3.10, MongoDB &ge; 5, and OpenJDK &ge; 8.

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
