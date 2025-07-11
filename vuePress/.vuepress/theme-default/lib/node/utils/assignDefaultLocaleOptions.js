export const DEFAULT_LOCALE_OPTIONS = {
    // color mode
    colorMode: 'auto',
    colorModeSwitch: true,
    // navbar
    navbar: [],
    logo: null,
    repo: null,
    selectLanguageText: 'Languages',
    selectLanguageAriaLabel: 'Select language',
    // sidebar
    sidebar: 'heading',
    sidebarDepth: 2,
    // page meta
    editLink: true,
    editLinkText: 'Edit this page',
    lastUpdated: true,
    contributors: true,
    contributorsText: 'Contributors',
    // 404 page messages
    notFound: [
        `There's nothing here.`,
        `How did we get here?`,
        `That's a Four-Oh-Four.`,
        `Looks like we've got some broken links.`,
    ],
    backToHome: '返回首页',
    // a11y
    openInNewWindow: 'open in new window',
    toggleColorMode: 'toggle color mode',
    toggleSidebar: 'toggle sidebar',
};
export const DEFAULT_LOCALE_DATA = {
    // navbar
    selectLanguageName: 'English',
};
/**
 * Assign default options
 */
export const assignDefaultLocaleOptions = (localeOptions) => {
    localeOptions.locales ??= {};
    Object.assign(localeOptions, {
        ...DEFAULT_LOCALE_OPTIONS,
        ...localeOptions,
    });
    localeOptions.locales['/'] ??= {};
    Object.assign(localeOptions.locales['/'], {
        ...DEFAULT_LOCALE_DATA,
        ...localeOptions.locales['/'],
    });
};
