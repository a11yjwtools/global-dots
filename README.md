# Global Dots Symbol Finder

A website where anyone can build Global Dots cells and read them in their own language.

## What's in this repository

| File | Purpose | On the public website? |
|---|---|---|
| `index.html` | The Symbol Finder page | Yes |
| `Source/rules.txt` | The symbols (Section 5: `1 [WORD]=CELLS -`) | No, only the symbols go into `data.json` |
| `Source/symbol_meanings.json` | English meaning of multi-word keys (`HOLYSPIRIT` → `holy spirit`) | No |
| `Languages/languages.json` | Optional: language names, or `false` to hide a language | No |
| `Languages/<CODE>/dictionary.txt` | `English = translation` for each language | No |
| `build_site.py` | Builds `index.html` + `data.json` into `public/` | No |
| `.github/workflows/pages.yml` | Tells GitHub to run `build_site.py` and publish the site after every change | No |

## Turning the website on (once)

1. **Settings → Pages → Build and deployment → Source: GitHub Actions.**
2. Open the **Actions** tab. When “Publish Symbol Finder” shows a green tick, your link appears in **Settings → Pages**, usually `https://YOUR-USERNAME.github.io/REPOSITORY-NAME/`.
3. Optional: click ⚙️ next to **About** on the repository's main page and tick **Use your GitHub Pages website**, so the link shows on the front page.

**Private repository:** publishing a site from a private repository needs a paid GitHub plan (Pro, Team or Enterprise). On a free plan the repository must be public, and then anyone can read the files in it.

## Updating the data

**On github.com:** open the folder (for example `Languages/S`), click **Add file → Upload files**, drop in the new `dictionary.txt`, and click **Commit changes**. The site rebuilds itself and updates in 2–3 minutes. Watch the **Actions** tab for the green tick.

**New language** (for example Chinese, `ZH`):

1. Download the blank dictionary from the link at the bottom of the website. It lists every English meaning.
2. Change the first line to `# Chinese Language Dictionary (Language Code: ZH)` and write the translation after each `=`, for example `love = 爱`.
3. Save it as `Languages/ZH/dictionary.txt` and push or upload it.

That's all: every `Languages/<CODE>/dictionary.txt` appears on the site automatically. The name comes from the first line of the file. To use a different name, add `"ZH": "中文 (Chinese)"` to `Languages/languages.json`. To hide a language without deleting it, add `"ZH": false`.

Dictionaries can be saved as UTF-8, UTF-16 ("Unicode" in Notepad) or Chinese GB18030. A full-width `＝` or a Tab also works instead of `=`.

**Checking a dictionary:** after each push, open **Actions**, click the latest run and scroll to its summary. It shows how many symbols each language translates, which ones are still missing, and a ⚠️ warning if a dictionary doesn't match any symbol, for example when the left side isn't the English meaning.

**From the website (owner only):** click **Owner** at the bottom of the page and connect once with a GitHub access key:

1. GitHub → your picture → **Settings → Developer settings → Personal access tokens → Fine-grained tokens → Generate new token**.
2. **Repository access:** Only select repositories → this repository.
3. **Permissions → Repository permissions → Contents: Read and write.**
4. Generate the token, copy it, and paste it on the Owner page with the repository name (`YOUR-USERNAME/REPOSITORY-NAME`) and branch `main`.

Then you can drop in files, add or edit symbols and translations, and add languages. Every change is saved to GitHub and the site rebuilds automatically. The key is stored only in your browser: never share it, and click **Sign out on this browser** on shared computers.

## If the site doesn't update

Open the **Actions** tab. A red ✗ means the build failed: click it to see the message. The most common cause is that **Settings → Pages → Source** is not set to **GitHub Actions**.

## Visit statistics (private, optional)

The site can count visitors anonymously with **Umami**, a privacy-friendly service with no cookies and a free plan. Only you see the numbers.

1. Create a free account at https://cloud.umami.is and choose **Add website**, using your site's address (for example `a11yjwtools.github.io`).
2. Copy the **Website ID** (it looks like `1a2b3c4d-…`).
3. Paste it into `Source/analytics.json` between the quotes after `"umami_website_id":`, then commit and push.

Your Umami dashboard then shows:

- new and returning visitors, and how long visits last
- each visitor's country, device and browser language
- these events:
  - **Translate**: which language people translate into
  - **Choose language**: when someone switches the site language (English, Español, Português, 中文)
  - **Open browse / Open learn**: which parts of the site people use

To switch statistics off, empty the id again.
