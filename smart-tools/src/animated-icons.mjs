const paths={
 pdf:'<path d="M7 3h7l4 4v14H6V3z"/><path d="M14 3v5h5"/><path class="auf-icon-detail" d="M9 12h6M9 16h6"/>',
 image:'<rect x="3" y="4" width="18" height="16" rx="3"/><circle class="auf-icon-detail" cx="8" cy="9" r="1.5"/><path d="m4 18 5-5 4 3 3-4 5 6"/>',
 business:'<rect x="3" y="7" width="18" height="14" rx="3"/><path d="M8 7V4h8v3M3 12c5 4 13 4 18 0"/><path class="auf-icon-detail" d="M10 13h4v4h-4z"/>',
 ai:'<path class="auf-icon-detail" d="m12 3 2.6 6.4L21 12l-6.4 2.6L12 21l-2.6-6.4L3 12l6.4-2.6z"/><path d="m19 2 .8 2.2L22 5l-2.2.8L19 8l-.8-2.2L16 5l2.2-.8z"/>',
 developer:'<path d="m8 6-6 6 6 6m8-12 6 6-6 6"/><path class="auf-icon-detail" d="m14 4-4 16"/>'
};
export function animatedIcon(category){return `<svg class="auf-animated-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">${paths[category]||paths.ai}</svg>`}
