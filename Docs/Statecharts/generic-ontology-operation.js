import { createMachine } from 'xstate';


const ontologyMachine = createMachine({
    id: 'ontology',
    initial: 'pending',
    states: {
        pending: {
            on: {
                perform_ontology_operation: [
                    { target: "awaitAcquireLock" }
                ],
                perform_ontology_backup: [
                    { target: "awaitAcquireLock" }
                ]
            }
        },
        awaitAcquireLock: {
            on: {
                acquire_lock: [
                    { target: "awaitPerformOperation" }
                ]
            }
        },
        awaitPerformOperation: {
            on: {
                perform_operation: [
                    { target: "awaitReleaseLock" }
                ]
            }
        },
        awaitReleaseLock: {
            on: {
                release_lock: [
                    { target: "pending" }
                ]
            }
        }
    }
});