import './app.css'
// import App from './App.svelte'

import App_new from './App_new.svelte';
import { mount } from 'svelte';

import { globalRefs } from './global_ref';

// const app = new App({
//   target: document.getElementById('app'),
// })

// const app = mount(App, { target: document.getElementById("app") });
const app = mount(App_new, { target: document.getElementById("app") });

export default app
