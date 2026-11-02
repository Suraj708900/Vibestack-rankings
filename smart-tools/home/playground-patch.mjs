const icon=paths=>`<svg class="hpg-ui-icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false">${paths}</svg>`;
export function patchPlayground(html){
 if(html.includes('data-composer-refresh'))return html;
 const chat=icon('<path d="M20 11a8 8 0 0 1-8 8H5l-3 3V11a9 9 0 0 1 18 0z"/><path d="M7 10h8M7 14h5"/>');
 const agent=icon('<rect x="4" y="7" width="16" height="13" rx="4"/><path d="M12 3v4M9 12h.01M15 12h.01M8 16h8"/>');
 const send=icon('<path d="M12 19V5m-6 6 6-6 6 6"/>');
 const required=['aria-selected="true">Chat</button>','aria-selected="false">Agent</button>','<button type="submit">Send</button>'];
 for(const value of required)if(!html.includes(value))throw Error('Expected playground control missing');
 html=html.replace(required[0],`aria-selected="true">${chat}Chat</button>`).replace(required[1],`aria-selected="false">${agent}Agent</button>`).replace(required[2],`<button type="submit" aria-label="Send message" title="Send message">${send}</button>`);
 html=html.replace('placeholder="Ask anything… e.g. which database for a SaaS MVP?"','placeholder="Ask AIUseFlow anything…"');
 html=html.replace('<p class="hpg-fine">','<p class="hpg-fine"><span class="hpg-ai-note">AI can make mistakes. Check important replies.</span>');
 return html.replace('</head>','<link rel="stylesheet" href="/assets/aiuseflow-home-v4/playground-composer-v1.css" data-composer-refresh></head>');
}
