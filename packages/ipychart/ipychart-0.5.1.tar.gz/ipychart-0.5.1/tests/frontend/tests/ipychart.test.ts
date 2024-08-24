// Copyright (c) Jupyter Development Team.
// Distributed under the terms of the Modified BSD License.

import { test } from '@jupyterlab/galata';
import { expect, Locator } from '@playwright/test';
import * as path from 'path';

async function sleep(time: number) {
    return await new Promise((resolve) => setTimeout(resolve, time));
}

test.describe('Widget Visual Regression', () => {
    test.beforeEach(async ({ page, tmpPath }) => {
        await page.contents.uploadDirectory(path.resolve(__dirname, './notebooks'), tmpPath);
        await page.filebrowser.openDirectory(tmpPath);
    });

    test('Run notebook ipychart-test-notebook.ipynb and capture cell outputs', async ({
        page,
        tmpPath,
    }) => {
        const notebook = 'ipychart-test-notebook.ipynb';
        await page.notebook.openByPath(`${tmpPath}/${notebook}`);
        await page.notebook.activate(notebook);
        await page.waitForTimeout(500);

        await page.notebook.runCellByCell({
            onAfterCellRun: async (cellIndex: number) => {
                await page.waitForTimeout(1500)
                const cell = await page.notebook.getCellOutputLocator(cellIndex);

                if (cell) {
                    const box = await cell.boundingBox();
                    if (box) {
                        await cell.waitFor({ state: 'visible' });
                        const image = `${notebook}-cell-${cellIndex}.png`;
                        await expect(cell).toHaveScreenshot(image, {
                            threshold: 0.5,
                            maxDiffPixelRatio: 0.03,
                            animations: "disabled",
                        });
                    }
                }
            },
        });

        await page.notebook.save();
    });
});
