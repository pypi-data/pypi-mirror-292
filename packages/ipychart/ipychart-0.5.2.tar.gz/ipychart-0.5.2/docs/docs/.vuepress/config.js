module.exports = (ctx) => ({
    title: 'ipychart',
    description: 'A Jupyter - Chart.js bridge enabling interactive data visualization with Python.',
    base: '/ipychart/',
    dest: '../public',
    head: [
        ['link', { rel: 'icon', href: '/favicon.ico' }],
        ['link', { rel: 'apple-touch-icon', sizes: '180x180', href: '/apple-touch-icon.png' }],
        ['link', { rel: 'manifest', href: '/site.webmanifest' }],
        ['link', { rel: 'mask-icon', href: '/safari-pinned-tab.svg', color: '#36a3ec' }],
        ['meta', { name: 'msapplication-TileImage', content: '/mstile-150x150.png' }],
        ['meta', { name: 'msapplication-TileColor', content: '#2b5797' }],
        ['meta', { name: 'theme-color', content: '#ffffff' }],
        ['meta', { name: 'google-site-verification', content: '6adHIzAVfLnUkGR5FwaEWZAyHGUHaTmI8W3nejcniAQ' }],
    ],
    plugins: [['flexsearch', { maxSuggestions: 8 }]],

    themeConfig: {
        repo: 'https://github.com/nicohlr/ipychart',
        editLinks: false,
        docsDir: 'docs',
        logo: '/ipychart-logo.png',

        smoothScroll: true,
        nav: [
            {
                text: 'User Guide',
                link: '/user_guide/introduction',
            },
            {
                text: 'Developer Guide',
                link: '/developer_guide/development_installation',
            },
        ],

        sidebar: [
            {
                title: 'User Guide',
                collapsable: false,
                sidebarDepth: 2,
                children: [
                    '/user_guide/introduction',
                    '/user_guide/getting_started',
                    '/user_guide/usage',
                    '/user_guide/charts',
                    '/user_guide/configuration',
                    '/user_guide/scales',
                    '/user_guide/pandas',
                    '/user_guide/advanced',
                ],
            },
            {
                title: 'Developer Guide',
                collapsable: false,
                sidebarDepth: 0,
                children: [
                    '/developer_guide/development_installation',
                    '/developer_guide/documentation',
                    '/developer_guide/publish',
                ],
            },
        ],
    },
});
