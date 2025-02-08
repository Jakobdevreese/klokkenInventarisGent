# Use Case 5 - Add a New Bell

## Actors

- Administrator
- Data Manager

## Stakeholders

- Public Users
- Carillon Association
- Researcher

## Goal

Create a new bell entery in the system database.

## Preconditions

- The user is authenticated and has the necessary permissions to add a record.

## Postconditions

The bell is added, vieable and searchable in the system.

## Main Success Scenario

1. `Data Manager` want to add a new bell.
2. `System` shows the neassecary fields according to DR_ADD_BELL.
3. `Data Manager` provides the required fields.
4. `System` validates the inputs.
5. `System` shows the new bell and a success message.

## Alternative Flows

### 4A - Wrong or missing information

1. The `system` shows an appropriate error message.
2. Back to step 2 in the Main Success Scenario.

### 4B - Missing record in the foreign keys

1. The `system` asks to add a new entery for the relevant foreing key (manifacturer, tower, carillon)
2. The flow returns to 5 after validation.

## Domain Specific Rules

### DR_BELL_DETAILS

A bell has the following info:

- Name
- Year
- Pitch
- Weight
- Ornaments
- Function
- Manufacturer*
- Carillon*
- Location*
- Location comments
- Comments

(*) are foreign keys.
