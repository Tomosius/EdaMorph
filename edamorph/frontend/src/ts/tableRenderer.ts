// tableRenderer.ts

import { Table, tableFromIPC } from "apache-arrow";

/**
 * TableDisplayOptions
 * -------------------
 * Interface for controlling table rendering, pagination, and visible columns.
 */
export interface TableDisplayOptions {
  /**
   * DOM element ID where the rendered HTML table will be injected.
   */
  domId: string;

  /**
   * List of columns to display by name.
   * If not specified, all columns will be displayed.
   */
  visibleColumns?: string[];

  /**
   * Number of rows to show per page (default: 50).
   */
  rowPageSize?: number;

  /**
   * Number of columns to show per page (optional).
   */
  colPageSize?: number;

  /**
   * Index of the current row page (zero-based, default: 0).
   */
  rowPage?: number;

  /**
   * Index of the current column page (zero-based, default: 0).
   */
  colPage?: number;
}

/**
 * Render an Apache Arrow Table to an HTML <table> with paging/toggling support.
 *
 * @param table    Arrow Table to render
 * @param options  Display and pagination settings (TableDisplayOptions)
 */
export function renderArrowTable(
  table: Table,
  options: TableDisplayOptions
): void {
  const {
    domId,
    visibleColumns,
    rowPageSize = 50,
    colPageSize,
    rowPage = 0,
    colPage = 0,
  } = options;

  // 1. Determine columns to show
  const allColumns = table.schema.fields.map(f => f.name);
  let colsToShow = visibleColumns || allColumns;
  let colOffset = colPageSize ? colPage * colPageSize : 0;
  let colsPage = colPageSize
    ? colsToShow.slice(colOffset, colOffset + colPageSize)
    : colsToShow;

  // 2. Calculate row range
  const totalRows = table.numRows;
  const rowOffset = rowPage * rowPageSize;
  const rowsToShow = Math.min(rowPageSize, totalRows - rowOffset);

  // 3. Build HTML
  let html = "<table><thead><tr>";
  for (const col of colsPage) html += `<th>${col}</th>`;
  html += "</tr></thead><tbody>";
  for (let i = 0; i < rowsToShow; i++) {
    html += "<tr>";
    for (const col of colsPage) {
      const columnVec = table.getChild(col); // Arrow >=10 API
      html += `<td>${columnVec?.get(i + rowOffset) ?? ""}</td>`;
    }
    html += "</tr>";
  }
  html += "</tbody></table>";

  // 4. Inject HTML
  const elem = document.getElementById(domId);
  if (elem) {
    elem.innerHTML = html;
  } else {
    console.warn(`renderArrowTable: Element with id '${domId}' not found.`);
  }
}

/**
 * Utility: Get all column names from Arrow Table
 */
export function getAllArrowColumns(table: Table): string[] {
  return table.schema.fields.map(f => f.name);
}

/**
 * Utility: Fetch Arrow Table from a backend URL (Arrow IPC format)
 */
export async function fetchArrowTable(url: string): Promise<Table> {
  const resp = await fetch(url);
  const buf = await resp.arrayBuffer();
  return tableFromIPC(buf);
}