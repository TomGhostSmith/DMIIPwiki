import { defaultTheme } from './theme-default'
import { defineUserConfig } from 'vuepress/cli'
import { viteBundler } from '@vuepress/bundler-vite'
import { searchPlugin } from '@vuepress/plugin-search'

export default defineUserConfig({
  lang: 'en-US',

  title: 'DMIIP',
  description: 'Wiki for DMIIP Lab at ISTBI, Fudan University',

  theme: defaultTheme({
    logo: 'resources/ISTBI.png',
    home: '/wiki/',
    navbar: ['/wiki/', '/wiki/seminar'],
  }),

  plugins: [
    searchPlugin({
      locales: {
        '/': {
          placeholder: 'Search...',
        },
      },
    }),
  ],
  // layout: 'ayouts/LayoutHome.vue',

  bundler: viteBundler(),


  // chainWebpack(config) {
  //   // Custom Vue configuration to avoid custom element detection
  //   config.module
  //     .rule('vue')
  //     .use('vue-loader')
  //     .tap(options => {
  //       options.compilerOptions = {
  //         ...options.compilerOptions,
  //         isCustomElement: tag => tag === 'Hello' // Exclude Hello from being treated as a custom element
  //       };
  //       return options;
  //     });
  // },
})

// import { createPage } from 'vuepress/core'
// export default defineUserConfig({
//     title: 'DMIIP',
//   description: 'A website for DMIIP at ISTBI, Fudan University',
//     // onInitialized: async (app) => {
//     //     app.pages.push(await createPage(app, {
//     //         path: '/friends.html',
//     //         frontmatter: {
//     //             layout: 'Friends',
//     //         },
//     // }))
//   // }
// })