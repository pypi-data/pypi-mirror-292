
// bun run vitest "src/lib/trucks/verify_3.vitest.js"

import { build_truck } from './index'
	
import { describe, it, expect } from 'vitest';
import assert from 'assert'

import _set from 'lodash/set'

describe ("trucks", () => {
	it ("can modify deep fields", async () => {
		const trucks = {}
		trucks [1] = build_truck ({
			freight: {
				1: {
					2: {
						3: ""
					}
				}
			}
		})
		
		let monitor = trucks [1].monitor (({ freight }) => {
			console.log ({ freight })
		})
		
		
		
		trucks [1].freight [1] = {
			2: {
				3: "freight"
			}
		}
		assert.equal (trucks [1].retrieve_change_count (), 1), trucks [1].retrieve_change_count ()
		assert.equal (trucks [1].freight[1][2][3], "freight")
		assert.deepEqual (
			trucks [1].freight [1], 
			{
				2: {
					3: "freight"
				}
			}
		)
		
		
		
		trucks [1].freight [1] = {
			3: {
				4: "freight"
			}
		}
		assert.equal (trucks [1].retrieve_change_count (), 2), trucks [1].retrieve_change_count ()
		assert.deepEqual (
			trucks [1].freight [1], 
			{
				3: {
					4: "freight"
				}
			}
		)
		
		delete trucks [1]
	})

})