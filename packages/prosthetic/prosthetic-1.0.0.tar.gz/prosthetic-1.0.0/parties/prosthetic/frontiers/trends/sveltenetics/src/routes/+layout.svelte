

<script lang="ts">

import { onMount, onDestroy, beforeUpdate } from 'svelte'
import { fade } from 'svelte/transition';
//
import { initializeStores, Modal, Toast } from '@skeletonlabs/skeleton';
import { storePopup } from '@skeletonlabs/skeleton';
import { TabGroup, Tab, TabAnchor } from '@skeletonlabs/skeleton';
import { Drawer, getDrawerStore } from '@skeletonlabs/skeleton';
import { setInitialClassState, autoModeWatcher } from '@skeletonlabs/skeleton';
import { LightSwitch } from '@skeletonlabs/skeleton';
import { page } from '$app/stores';
//
import { computePosition, autoUpdate, offset, shift, flip, arrow } from '@floating-ui/dom';
//
import "../app.css";
//


import {
	lease_behavior_truck,
	give_back_behavior_truck
} from '$lib/Behavior/Trucks'


storePopup.set ({ computePosition, autoUpdate, offset, shift, flip, arrow });			
initializeStores ();

let behavior_truck_leased = "no"
onMount (async () => {
	autoModeWatcher ();
	setInitialClassState ()
	
	lease_behavior_truck ()
	behavior_truck_leased = "yes"
})
onDestroy (async () => {
	give_back_behavior_truck ()
	behavior_truck_leased = "no"
})



</script>

{#if behavior_truck_leased === "yes" }
<div 
	in:fade={{ duration: 500 }} 
	class="app"
	style="
		display: flex;
		flex-direction: column;
		min-height: 100vh;
		margin: 0;
		padding: 0;
	"
>	
	<div style="text-align: center">prosthetic</div>

	<TabGroup 
		justify="justify-center"
		active="variant-filled-primary"
		hover="hover:variant-soft-primary"
		flex="flex-1 lg:flex-none"
		rounded=""
		border=""
	>
		<TabAnchor 
			href="/trends" 
			selected={ $page.url.pathname.indexOf ('/trends') === 0 }
		>
			<span>Trends</span>
		</TabAnchor>
		<TabAnchor 
			href="/treasures" 
			selected={ $page.url.pathname.indexOf ('/treasures') === 0 }
		>
			<span>Treasures</span>
		</TabAnchor>
	</TabGroup>
	
	
	<div
		style="
			display: flex;
			flex-direction: column;
			min-height: 100%;
		"
	>
		<main style="min-height: 100vh">
			<slot></slot>
		</main>
		
		<hr class="!border-t-8 !border-double" />
	</div>
</div>
{/if}



<style>
	main {
		flex: 1;
		display: flex;
		flex-direction: column;
		padding: 1rem;
		width: 100%;
		max-width: 64rem;
		margin: 0 auto;
		box-sizing: border-box;
	}

	footer {
		display: flex;
		flex-direction: column;
		justify-content: center;
		align-items: center;
		padding: 12px;
	}
	
	@media (min-width: 480px) {
		footer {
			padding: 12px 0;
		}
	}
</style>