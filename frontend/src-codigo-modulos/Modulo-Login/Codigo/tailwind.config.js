module.exports = {
    content: ["./src/**/*.{html,js,ts,jsx,tsx}"],
    corePlugins: { preflight: true },
    theme: {
        extend: {
            colors: {
                "dark-50": "var(--dark-50)",
                "variable-collection-blue": "var(--variable-collection-blue)",
                "variable-collection-dark-shade-25":
                    "var(--variable-collection-dark-shade-25)",
                "variable-collection-dark-shade-5":
                    "var(--variable-collection-dark-shade-5)",
                "variable-collection-dark-shade-50":
                    "var(--variable-collection-dark-shade-50)",
                "variable-collection-dark-shade-75":
                    "var(--variable-collection-dark-shade-75)",
                "variable-collection-error": "var(--variable-collection-error)",
                "variable-collection-green": "var(--variable-collection-green)",
                "variable-collection-orange": "var(--variable-collection-orange)",
                "variable-collection-primary": "var(--variable-collection-primary)",
                "variable-collection-secondary": "var(--variable-collection-secondary)",
                "variable-collection-tertiary": "var(--variable-collection-tertiary)",
                "variable-collection-text": "var(--variable-collection-text)",
            },
            fontFamily: {
                "custom-body": "var(--custom-body-font-family)",
                "custom-title-h1": "var(--custom-title-h1-font-family)",
                "custom-title-h2": "var(--custom-title-h2-font-family)",
                "custom-title-h3": "var(--custom-title-h3-font-family)",
                "custom-title-h4": "var(--custom-title-h4-font-family)",
                "custom-title-h5": "var(--custom-title-h5-font-family)",
                "custom-title-h6": "var(--custom-title-h6-font-family)",
            },
        },
    },
    plugins: [],
};
