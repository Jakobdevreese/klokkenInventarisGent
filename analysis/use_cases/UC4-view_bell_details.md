# Use Case 4 - View Bell Details

## Actors

- Public User (visitor)
- Researcher

## Stakeholders

- Admins
- Carillon Association

## Goal

Inspect detailed information about a specific bell, including pitch, weight, year of cating, ornaments, profile, and functions.

## Preconditions

- The Public User found a specific bell through browsing a carillon, or via the search.

## Postconditions

The Public User found information on the desired bell.

## Main Success Scenario

1. `Public User` asks for information on a specific bell.
2. `System` retrieves all the available information.
3. `System` displays bell details following DR_BELL_DETAILS.
4. `Public User` can see references to the bell's manufacturer, location, and andy associated carillon.

## Alternative Flows

- **Bell Not Found**: If the bell has been removed or the ID is invalid, an error or “Bell not found” is displayed.

## Domain Specific Rules

### DR_BELL_DETAILS

A bell has the following info:

- Name
- Year
- Pitch
- Weight
- Ornaments
- Function
- Manufacturer
- Carillon
- Location
- Location comments
- Comments
- Related files (images, articles, sound fragments)