


/*	
import {
	lease_behavior_truck,
	give_back_behavior_truck
} from '$lib/Behavior/Trucks'

*/

/*	
import { onMount, onDestroy } from 'svelte'
import { check_behavior_truck, monitor_behavior_truck } from '$lib/Behavior/Trucks'

let RT_Prepared = "no"
let RT_Monitor;
let RT_Freight;
onMount (async () => {
	const Truck = check_behavior_truck ()
	RT_Freight = Truck.freight; 
	
	RT_Monitor = monitor_behavior_truck ((_freight) => {
		RT_Freight = _freight;
	})
	
	RT_Prepared = "yes"
});

onDestroy (() => {
	RT_Monitor.stop ()
}); 

// RT_Freight.net_path
// RT_Freight.net_name
*/


/*	
import { ask_for_freight } from '$lib/Behavior/Trucks'
const { mongo_address } = ask_for_freight ();
*/

import * as AptosSDK from "@aptos-labs/ts-sdk";
import { build_truck } from '$lib/trucks'
const trucks = {}

export const lease_behavior_truck = () => {
	const net_path = "https://api.mainnet.aptoslabs.com/v1"
	
	let origin_address = window.location.protocol + '//' + window.location.host
	
	trucks [1] = build_truck ({
		freight: {
			origin_address
		}
	})
}

export const ask_for_freight = () => {
	return trucks [1].freight;
}

export const give_back_behavior_truck = () => {
	delete trucks [1];
}

export const check_behavior_truck = () => {
	return trucks [1];
}
export const monitor_behavior_truck = (action) => {	
	return trucks [1].monitor (({ freight }) => {
		console.info ('Behavior Truck_Monitor', { freight })
		action (freight);
	})
}







