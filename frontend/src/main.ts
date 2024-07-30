import './app.css'
import App from './App.svelte'
import { mount } from 'svelte';

import { globalRefs } from './global_ref';

// const app = new App({
//   target: document.getElementById('app'),
// })

const app = mount(App, { target: document.getElementById("app") });

export default app
