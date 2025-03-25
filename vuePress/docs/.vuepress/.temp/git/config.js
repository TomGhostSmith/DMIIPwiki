import { GitContributors } from "E:/5-Doctorate/y-servers/DMIIPwiki/wiki/node_modules/@vuepress/plugin-git/lib/client/components/GitContributors.js";
import { GitChangelog } from "E:/5-Doctorate/y-servers/DMIIPwiki/wiki/node_modules/@vuepress/plugin-git/lib/client/components/GitChangelog.js";

export default {
  enhance: ({ app }) => {
    app.component("GitContributors", GitContributors);
    app.component("GitChangelog", GitChangelog);
  },
};
