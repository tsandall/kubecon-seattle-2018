package petstore.authz

import data.petstore.tickets

default allow = false

# Allow customers to access their own accounts.
allow = true {
    input.method = "GET"
    input.path = ["accounts", user_name]
    input.subject.user = user_name
}

# Allow support to access accounts of customers they're assisting.
allow = true {
    input.method = "GET"
    input.path = ["accounts", user_name]
    input.subject.groups[_] = "customer-service"
    input.subject.user = tickets[user_name][_].assignee
}
