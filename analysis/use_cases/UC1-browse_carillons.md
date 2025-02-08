# Use Case 1 - Browse Carillons

## Actors

- Public User (visitor)
- Researcher

## Stakeholders

- Admins
- Carillon Association

## Goal

View all documented carillons in the database, including basic details such as name, location, and status (active, historical, etc.)

## Preconditions

- The system has at least one carillon in the database.
- The user has accessed the application's homepage or a dedicated "carillon" page.

## Postconditions

The Public User viewed the desired carillons.

## Main Success Scenario

1. `Public User` navigates to the carillon listing page.
2. `System` retrieves a list of carillons from the database.
3. `System` displays each carillon's name, location and status.
4. `Public User` can optionally view more specific information and details on each carillon.

## Alternative Flows

- **No Carillons**: If no carillons exist in the database, the system shows a "No carillons found" message.

