<?php
// Enable error reporting for debugging (for development)
error_reporting(E_ALL);
ini_set('display_errors', 1);

// Set the content type to JSON
header('Content-Type: application/json');

// Initialize response array
$response = array();

// Get the raw POST data
$inputData = json_decode(file_get_contents("php://input"), true);

// Check if player data is provided
if (isset($inputData['player1']) && isset($inputData['player2'])) {
    $player1 = $inputData['player1'];
    $player2 = $inputData['player2'];

    // Connect to PostgreSQL database
    $dbconn = pg_connect("host=localhost dbname=darts user=dart_thrower password=darts");

    if (!$dbconn) {
        $response['status'] = 'error';
        $response['message'] = 'Failed to connect to the database';
    } else {
        // Start the game and insert the game record
        $query = "INSERT INTO games DEFAULT VALUES RETURNING id";
        $result = pg_query($dbconn, $query);

        if ($result) {
            // Fetch the game_id from the result
            $row = pg_fetch_assoc($result);
            $game_id = $row['id'];

            // Set success response
            $response['status'] = 'success';
            $response['game_id'] = $game_id;
        } else {
            // Handle error creating the game
            $response['status'] = 'error';
            $response['message'] = 'Error creating the game.';
        }

        // Close the database connection
        pg_close($dbconn);
    }
} else {
    // Missing player data
    $response['status'] = 'error';
    $response['message'] = 'Missing player data';
}

// Send the JSON response
echo json_encode($response);
?>
