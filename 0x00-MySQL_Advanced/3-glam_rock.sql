-- Selects bands with Glam Rock as their
-- style and ranks them by their longevity
SELECT band_name,
IFNULL(split, 2022) - formed AS lifespan
FROM metal_bands
WHERE FIND_IN_SET('Glam rock', IFNULL(style, ''))
ORDER BY lifespan DESC;
