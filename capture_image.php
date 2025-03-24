<?php
// Set the content type to JSON
header('Content-Type: application/json');

// Get the raw POST data
$inputData = json_decode(file_get_contents("php://input"), true);

// Check if the image and player are provided
if (isset($inputData['image']) && isset($inputData['player'])) {
    $image = $inputData['image'];  // This is the base64-encoded image data
    $player = $inputData['player'];

    // Connect to PostgreSQL database
    $dbconn = pg_connect("host=localhost dbname=darts user=dart_thrower password=darts");

    if (!$dbconn) {
        echo json_encode(['status' => 'error', 'message' => 'Failed to connect to the database']);
        exit;
    }

    // Save the image to the database
    $query = "UPDATE games SET image = $1 WHERE player1 = $2 OR player2 = $2";
    $result = pg_query_params($dbconn, $query, array($image, $player));

    if ($result) {
        echo json_encode(['status' => 'success', 'message' => 'Image captured and saved successfully']);
    } else {
        echo json_encode(['status' => 'error', 'message' => 'Failed to save image']);
    }

    // Close the connection
    pg_close($dbconn);
} else {
    echo json_encode(['status' => 'error', 'message' => 'Missing image or player data']);
}
?>