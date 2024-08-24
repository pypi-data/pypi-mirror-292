// This code comes from the chartjs-plugin-colorschemes package.
// The original code of this package is not compatible with chart.js 3.x.
// Therefore, the code has been adapted to work with chart.js 3.x and integrated into ipychart.
// To see the original version of this file, please visit:
// https://github.com/nagix/chartjs-plugin-colorschemes/blob/master/src/plugins/plugin.colorschemes.js

import Chart, { ChartDataset, Plugin, ChartConfiguration, ChartType } from 'chart.js/auto';
import { isArray } from 'chart.js/helpers';

const EXPANDO_KEY = '$colorschemes';

function addAlpha(hex: string): string {
    if (!/^#([A-Fa-f0-9]{3}){1,2}$/.test(hex)) {
        throw new Error('Bad Hex');
    }

    // Expand shorthand hex code to full form
    let c = hex.substring(1).split('');
    if (c.length === 3) {
        c = [c[0], c[0], c[1], c[1], c[2], c[2]];
    }

    // Convert hex code to a number
    const hexValue = parseInt(c.join(''), 16);

    // Extract RGB values and return rgba string
    const r = (hexValue >> 16) & 255;
    const g = (hexValue >> 8) & 255;
    const b = hexValue & 255;

    return `rgba(${r}, ${g}, ${b}, 0.5)`;
}

function getScheme(scheme: string | any[]): any[] | null {
    if (isArray(scheme) || scheme === null) {
        return scheme;
    }
    if (typeof scheme === 'string') {
        const colorschemes = (Chart as any).colorschemes || {};
        const arr = scheme.split('.');
        const category = colorschemes[arr[0]];
        return category[arr[1]];
    }
    return null;
}

const ColorSchemesPlugin: Plugin<
    'line' | 'bar' | 'radar' | 'scatter' | 'doughnut' | 'pie' | 'polarArea'
> = {
    id: 'colorschemes',

    beforeUpdate(chart, args, options: any) {
        if (options === undefined) {
            options = args;
        }

        const scheme = getScheme(options.scheme);
        const reverse = false;
        const override = true;
        let length: number;
        let colorIndex: number;
        let colorCode: string;

        if (scheme) {
            length = scheme.length;

            // Set scheme colors
            chart.config.data.datasets.forEach(
                (dataset: ChartDataset<ChartType>, datasetIndex: number) => {
                    colorIndex = datasetIndex % length;
                    colorCode = scheme[reverse ? length - colorIndex - 1 : colorIndex];

                    // Object to store which color option is set
                    (dataset as any)[EXPANDO_KEY] = {};

                    const chartType = (chart.config as ChartConfiguration).type;

                    switch (dataset.type || chartType) {
                        case 'line':
                        case 'radar':
                        case 'scatter':
                            if (typeof dataset.backgroundColor === 'undefined' || override) {
                                (dataset as any)[EXPANDO_KEY].backgroundColor =
                                    dataset.backgroundColor;
                                dataset.backgroundColor = addAlpha(colorCode);
                            }
                            if (typeof dataset.borderColor === 'undefined' || override) {
                                (dataset as any)[EXPANDO_KEY].borderColor = dataset.borderColor;
                                dataset.borderColor = colorCode;
                            }
                            // Ensure the dataset has point-specific properties
                            if (
                                dataset.type === 'line' ||
                                dataset.type === 'radar' ||
                                dataset.type === 'scatter'
                            ) {
                                const lineDataset = dataset as ChartDataset<
                                    'line' | 'radar' | 'scatter'
                                >;
                                if (
                                    typeof lineDataset.pointBackgroundColor === 'undefined' ||
                                    override
                                ) {
                                    (dataset as any)[EXPANDO_KEY].pointBackgroundColor =
                                        lineDataset.pointBackgroundColor;
                                    lineDataset.pointBackgroundColor = addAlpha(colorCode);
                                }
                                if (
                                    typeof lineDataset.pointBorderColor === 'undefined' ||
                                    override
                                ) {
                                    (dataset as any)[EXPANDO_KEY].pointBorderColor =
                                        lineDataset.pointBorderColor;
                                    lineDataset.pointBorderColor = colorCode;
                                }
                            }
                            break;

                        case 'doughnut':
                        case 'pie':
                        case 'polarArea':
                            if (typeof dataset.backgroundColor === 'undefined' || override) {
                                (dataset as any)[EXPANDO_KEY].backgroundColor =
                                    dataset.backgroundColor;
                                dataset.backgroundColor = dataset.data.map(
                                    (_: any, dataIndex: number) => {
                                        colorIndex = dataIndex % length;
                                        return scheme[
                                            reverse ? length - colorIndex - 1 : colorIndex
                                        ];
                                    }
                                );
                            }
                            break;

                        case 'bar':
                            if (typeof dataset.backgroundColor === 'undefined' || override) {
                                (dataset as any)[EXPANDO_KEY].backgroundColor =
                                    dataset.backgroundColor;
                                dataset.backgroundColor = colorCode;
                            }
                            if (typeof dataset.borderColor === 'undefined' || override) {
                                (dataset as any)[EXPANDO_KEY].borderColor = dataset.borderColor;
                                dataset.borderColor = colorCode;
                            }
                            break;

                        default:
                            if (typeof dataset.backgroundColor === 'undefined' || override) {
                                (dataset as any)[EXPANDO_KEY].backgroundColor =
                                    dataset.backgroundColor;
                                dataset.backgroundColor = colorCode;
                            }
                            break;
                    }
                }
            );
        }
    },

    afterUpdate(chart) {
        // Unset colors
        chart.config.data.datasets.forEach((dataset: ChartDataset<ChartType>) => {
            if ((dataset as any)[EXPANDO_KEY]) {
                if (
                    Object.prototype.hasOwnProperty.call(
                        (dataset as any)[EXPANDO_KEY],
                        'backgroundColor'
                    )
                ) {
                    dataset.backgroundColor = (dataset as any)[EXPANDO_KEY].backgroundColor;
                }
                if (
                    Object.prototype.hasOwnProperty.call(
                        (dataset as any)[EXPANDO_KEY],
                        'borderColor'
                    )
                ) {
                    dataset.borderColor = (dataset as any)[EXPANDO_KEY].borderColor;
                }
                if (
                    Object.prototype.hasOwnProperty.call(
                        (dataset as any)[EXPANDO_KEY],
                        'pointBackgroundColor'
                    )
                ) {
                    (dataset as any).pointBackgroundColor = (dataset as any)[
                        EXPANDO_KEY
                    ].pointBackgroundColor;
                }
                if (
                    Object.prototype.hasOwnProperty.call(
                        (dataset as any)[EXPANDO_KEY],
                        'pointBorderColor'
                    )
                ) {
                    (dataset as any).pointBorderColor = (dataset as any)[
                        EXPANDO_KEY
                    ].pointBorderColor;
                }
                delete (dataset as any)[EXPANDO_KEY];
            }
        });
    },
};

export default ColorSchemesPlugin;
