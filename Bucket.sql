CREATE VIEW Bucket AS
SELECT
    User.Username AS User_Name,
    Buckets.BucketName AS Bucket_Name,
    Buckets.BucketAllotted AS Bucket_Value_Allotted,
    Buckets.BucketRemaining AS Bucket_Value_Remaining,
    Transactions.TransDate AS Transaction_Date,
    Transactions.Description AS Transaction_Description,
    Transactions.Amount AS Transaction_Amount
FROM 
    User user
LEFT JOIN 
    Buckets Buckets ON User.UserID = Buckets.UserID
LEFT JOIN 
    Transactions Transactions ON Buckets.BucketID = Transactions.BucketID
