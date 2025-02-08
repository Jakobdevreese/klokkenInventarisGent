# Use Case 3 - Serach for Bells

## Actors

- Public User (visitor)
- Researcher

## Stakeholders

- Admins
- Carillon Association

## Goal

Search for bells by criteria such as pitch, manufacturer, year of casting or location.

## Preconditions

- The database contains at least one bell.

## Postconditions

The Public User found information on the desired bells.

## Main Success Scenario

1. `Public User` wants to search bells based on criteria.
2. `System` asks for search parameters following DR_BELL_SEARCH.
3. `Public User` enters search parameters.
4. `System` searches for bells matching the search criteria.
5. `System` shows a list of the retrieved bells.
6. `Public User` can select a bell from the result list to view more details.

## Alternative Flows

- **No Matching Results**: System displays "No bells found matching your criteria."

## Domain Specific Rules

### DR_BELL_SEARCH

User can search bells by:

- Name
- Year
- Location (Tower)
- Manufacturer
- Weight
- Pitch