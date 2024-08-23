
// bun run vitest "src/lib/trucks/index.vitest.js"

import { build_truck } from './index'
	
import { describe, it, expect } from 'vitest';
import assert from 'assert'

import _set from 'lodash/set'

describe ("trucks", () => {
	it ("is constant for story 1", async () => {
		const trucks = {}
		trucks [1] = build_truck ({
			freight: {
				unsigned_transaction_fields: {
					ICANN_net_path: "",
					from_address_hexadecimal_string: "",
					to_address_hexadecimal_string: "",
					amount_of_Octas: "",
					//
					transaction_expiration: ""
				},
				
				unsigned_transaction: {
					hexadecimal_string: "",
					Aptos_object: {},
					Aptos_object_fiberized: ""
				},
				signature: {
					hexadecimal_string: "",
					Aptos_object: {},
					Aptos_object_fiberized: ""
				}
			}
		})
		
		let monitor = trucks [1].monitor (({ freight }) => {
			assert.equal (
				trucks [1].freight ["unsigned_transaction_fields"] ["ICANN_net_path"],
				"another.path"
			)
			console.log ({ freight })
		})
		
		trucks [1].freight ["unsigned_transaction_fields"] ["ICANN_net_path"] = "another.path"
		
		assert.equal (trucks [1].monitors.length, 1), trucks [1].monitors
		
		delete trucks [1]
	})
	
	it ("is constant for story 2", async () => {
		const trucks = {}
		trucks [1] = build_truck ({
			freight: {
				unsigned_transaction_fields: {
					ICANN_net_path: ""
				}
			}
		})
		
		
		trucks [1].freight ["unsigned_transaction_fields"] ["ICANN_net_path"] = "another.path"
		console.log (trucks [1].freight)
		
		assert.equal (trucks [1].retrieve_change_count (), 1), trucks [1].retrieve_change_count ()
		
		trucks [1].freight ["unsigned_transaction_fields"] ["from_address_hexadecimal_string"] = "another.path"
		assert.equal (trucks [1].retrieve_change_count (), 2), trucks [1].retrieve_change_count ()
		
		delete trucks [1];
		
		console.log ({ trucks })
		console.log (trucks [1])
		
		assert.equal (trucks [1], undefined), trucks [1]
		
	})
})