CREATE VIEW Homepage AS
SELECT 
    User.Username AS User_Name,
    Buckets.BucketName AS Bucket_Name,
    Buckets.BucketDescription AS Bucket_Description,
    Buckets.BucketAllotted AS Bucket_Value_Allotted,
    Buckets.BucketRemaining AS Bucket_Value_Remaining,
    Transactions.Amount AS Transaction_Amount,
    Transactions.Description AS Transaction_Description,
    Transactions.TransDate AS Transaction_Date
FROM
    user User
LEFT JOIN 
    Buckets Buckets ON User.UserID = Buckets.UserID
LEFT JOIN 
    Transactions Transactions ON User.UserID = Transactions.UserID
GROUP BY 
    User_Name, BucketName, Transaction_Date
