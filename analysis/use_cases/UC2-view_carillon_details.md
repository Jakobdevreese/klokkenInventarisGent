# Use Case 2 - View Carillon Details

## Actors

- Public User (visitor)
- Researcher

## Stakeholders

- Admins
- Carillon Association

## Goal

Gain detailled information about a specific carillon (e.g., its founding date, its set of bells, any historical notes)

## Preconditions

- The Public User has selected a carillon from a list or performed a direct link to its detail page.

## Postconditions

The Public User viewed the desired carillon, and gained all the information on the carillon available in the database.

## Main Success Scenario

1. `Public User` asks the information on a specific carillon.
2. `System` retrieves the information from the database.
3. `System` displays all the information according to DR_CARILLON_DETAILS.
4. `Public User` can view each bell's basic info or navigate to a bell's individual detail page.

## Alternative Flows

- **Carillon Not Found**: If the carillon’s ID does not exist in the system, the user sees an error or a “Carillon not found” page.

## Domain Specific Rules

### DR_CARILLON_DETAILS

The database contains on each carillon the following information:

- Name
- Total number of bells
- Total weight
- Comments
- Transposition
- Pitch?
- Location