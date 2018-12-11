package example

import data.clinic.filtering

allow {
   input.method = "GET"
   input.path = ["pets"]
   filtering.details[pet]
}
