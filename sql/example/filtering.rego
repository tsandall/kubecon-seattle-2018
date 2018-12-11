package clinic.filtering

details[pet] {
    data.pets[pet]

    # Uncomment next line to filter pets to those owned by user.
    # pet.owner = input.subject.user
}

# Uncomment next rule to filter pets to those treated by the user.
#details[pet] {
#    data.pets[pet]
#    pet.veterinarian = input.subject.user
#    pet.clinic = input.subject.user
#}

# Example Pet Owners
# ------
#   bob
#   liz
#   john

# Example Veterinarians
# -------------
#   alice
#   terry

# Example Pet attributes
# --------------
#   veterinarian
#   clinic
#   owner

# input = {
#     "subject": {
#         "user": "bob",
#     }
# }

# input = {
#     "subject": {
#         "user": "alice",
#         "location": "Shady Bluffs",
#     }
# }
