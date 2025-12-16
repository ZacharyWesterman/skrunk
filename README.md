# Skrunk Server

<table>
<tr>
<td>

<!-- Optimized and recolored logo -->
<span align="left" style="filter: invert(57%) sepia(33%) saturate(791%) hue-rotate(117deg) brightness(99%) contrast(86%);">
<svg style="float:left;" xmlns="http://www.w3.org/2000/svg" width="118" height="121.684" viewBox="0 0 31.221 32.196">
<g stroke="#000" stroke-width=".266">
<path d="M7.786 11.47H9.11v1.322H7.786zM6.463 14.115h1.323v1.323H6.463zM6.463 16.761h1.323v1.323H6.463zM23.661 11.47h-1.323v1.322h1.323zM24.984 14.115h-1.323v1.323h1.323zM24.984 16.761h-1.323v1.323h1.323z"/>
</g>
<path stroke="#000" d="m345 360-51 88h11l6-10h68l6 10h10zm-.818 20v54h-8.819v-39zm1.728 0 8.738 15v39h-8.738zM334 397v37h-8.818v-22zm22 0 8.738 15v22H356Zm-32.182 17v20H315v-5zm42.272 0 8.738 15v5h-8.738z" transform="matrix(.26458 0 0 .19665 -75.558 -58.002)"/>
<g stroke="#000">
<path stroke-width=".131" d="M2.18 2.082 14.4 4.855 5.09 9.49H4.033l6.375-3.537-4.787 1.42H3.503l5.82-1.851H2.18z"/>
<path stroke-width=".13" d="m29.156 2.082-12.11 2.773 9.226 4.635h1.048l-6.317-3.537 4.744 1.42h2.098l-5.768-1.851h7.079z"/>
</g>
<path stroke="#000" stroke-width=".362" d="m15.723 12.792-3.307-3.969h6.615l-1.191 1.323-.53-.264-.793.793.265.794z"/>
</svg>

</span>
<!-- Alternative image for viewing in GitHub -->
<img src="data/logo.svg" align="left" alt="" style="filter: invert(57%) sepia(33%) saturate(791%) hue-rotate(117deg) brightness(99%) contrast(86%);" />

My home-built database solution for managing personal data and interacting with other projects.

</td>
</tr>
</table>

Current features include:
- Full support for modern Android/iOS mobile as well as desktop browsers.
- A fully featured library/book cataloging system: type the name of a book, click the correct match, then scan a QR code, barcode, or RFID tag. Bam, it's now cataloged under your name, and you can easily find it later, specify if someone's borrowing it, transfer ownership, etc.
- Arbitrary item inventory system: similar to books, but meant for catalogging stuff like tools, furniture, etc.
- File storage with advanced tagging functionality and minimal limitations. Want to upload 75 photos of your dog? Can do, just select them all and add the "dog" and "my-dog's-name" tags when uploading. Has it been 10 years and you can't find those images? Just search for your dog's name. Want to download all the results from that search? Just click the "download all" button. Don't want anyone else to see that video of you in a tutu? Just mark the file as "only visible to me".
- Allow users to report bugs, request new features, and see what features are planned or in progress.
- [Weather Alerts](https://github.com/ZacharyWesterman/weather-alerts) integration: if you moved, changed your phone number, want to change the default temperature thresholds, or just disable your alerts altogether, you can do so in the user settings page.
- Subsonic Music Server Integration: Search albums, and interact with the Library to show what books also have an audiobook version.
- Dynamic theme: If you don't like the default colors or styling, you can always change it in user settings.
- Data feeds: Allow the server to automatically fetch content from across the web, e.g. regularly-updated webcomics or serials; getting a guaranteed notification when new updates come out.
- Fine-grained user control:
  - User Isolation: Sometimes you don't want certain groups of users to interact (e.g. in-laws, different friend groups, etc). If that's the case, admins can assign a "group" to users. Any users not in the same group will not be able to see or interact with each other's data.
  - User Permissions: Control what type of actions users are allowed to do, and what they're allowed to see.
- Bot friendly: admins can generate API tokens to allow bots or other services to securely make requests. These tokens can have the same permissions restrictions applied to them as users! Check out the [Python API repo](https://github.com/ZacharyWesterman/skrunk_api) for a fast way to get started.

Every one of the above features is fully optional, and can be disabled from the admin options, on a per-group basis, and individually by each user.

---
### Setup

This application requires some flavor of Linux (tested on Ubuntu 22 and 24), Python ≥ 3.11, [Poetry](https://python-poetry.org/), MongoDB ≥ 5, and OpenJDK ≥ 8.

---

To get all set up, first install apt dependencies, then first download the repo, and install python dependencies.
In most cases you won't need the documentation to generate, so you can append `--without dev` to the install command.
```bash
sudo apt-get install libsasl2-dev python-dev-is-python3 libldap2-dev libssl-dev
git clone https://github.com/ZacharyWesterman/skrunk.git --recursive
cd skrunk
poetry install --no-root --without dev
```

If you plan to enable the file module, you'll want to make sure you have a place to store blob data that is uploaded to the site.
It can be any directory, but going forward we'll assume it's `/var/blob_data`.

Also, make sure you know the MongoDB URL of the database. If not specified at run-time, this will default to `localhost`.

---

To run this application with minimal params:
```bash
./run.sh --blob-path=/var/blob_data
```

Additional parameters are available. You can run `./run.sh --help` to see them all.
