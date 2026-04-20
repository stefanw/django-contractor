# Django Contractor

You need additional CSS/JS on your website, but don't want to include it in your Django project? Build it somewhere else, notify contractor via webhook and it will fetch the files from a URL into a versioned media directory. Then you can use them in your website like normal Django media files.

## Example with Github Pages + Django CMS

This is a basic example with static HTML, CSS and JavaScript, but it's easy to add a build pipeline too.

```html
<!-- index.html -->

<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div id="app">
        Hello World!
    </div>

    <script src="app.js" type="module"></script>
</body>
</html>
```

```js
// app.js
console.log("Hello World!");
```

```css
/* style.css */

#app {
    background: red;
}
```

> [!IMPORTANT]
> Your app will share all the global styles and scripts from the rest of the site where it will be embedded on. django-contractor provides no scoping for this.

> [!TIP]
> During development, it's handy to have the global styles and scripts present to see the final behavior. Make sure to not include them in your production build however, as that would include them twice on the page.

First, create a new repository. Then, using the Django admin, create a new Contract with the source URL `https://<org>.github.io/<repo>/`. To make `django-contractor` find the app's above files, enter the following into the Files field:

```
index.html
style.css
app.js?type=module
```

Add the app's assets to the root of your repository. Now, we'll add an action to publish the app to Github Pages:

```yaml
name: build

on:
  push:
    branches:
      - main
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: true

jobs:
  build:
    environment:
      name: github-pages
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6.0.2
      # run your build pipeline, e.g., vite
      # for this example, just copy the source files to a dist folder
      - name: Build the app
        run: mkdir -p dist && cp index.html style.css app.js dist
      - name: Setup Pages
        uses: actions/configure-pages@v6.0.0
      - name: Upload artifact
        uses: actions/upload-pages-artifact@v5.0.0
        with:
          path: ./dist
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v5.0.0

```

> [!IMPORTANT]
> In order for the action to run successfully, you need to set your repo's Pages source to "Github Actions". You can do this in your repo's settings under Pages → Build and deployment.

Push all the files to the repository and ensure you can see the content on Github Pages. In the Contract admin, run the "Manual update" action in order to fetch the remote files. The files field of the Contract should change after the files have been fetched; the JavaScript and CSS file should show a sha384 integrity hash.

To embed the app on your site, use the "Render contract work" CMS plugin. Select the contract, and enter `app.js` in the Javascript field, `style.css` in the styles field, and `index.html#//div[@id="app"]` in the xpath field. Save the plugin, and you should see your app!

> [!TIP]
> You can embed different sections of the HTML files using multiple CMS plugins. The JavaScript and CSS files will only ever be embedded once.

Lastly, to update the contract whenever the repo changes, add a Webhook in your repo's settings. Select the "Deployments" and "Page builds"  events and enter the webhook URL visible in the Contract admin.

> [!IMPORTANT]
> Make sure that "webhook active" is enabled for the contract. Otherwise, updating via webhook will fail.
