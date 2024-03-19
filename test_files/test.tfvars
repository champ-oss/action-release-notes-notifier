image_abc = "123456789012.dkr.ecr.us-east-1.amazonaws.com/abc-client:72055d15b8a9a8bf2c6a39bbe919ee528ad15200"
image_def = "123456789012.dkr.ecr.us-east-1.amazonaws.com/def-client:2af48902b475eed251939609892a5db12bef5551"
image_ghi = "123456789012.dkr.ecr.us-east-1.amazonaws.com/ghi-client:75ea3c7265ef1bf821397f88e8d42efdeea9561e"
image_jkl = "123456789012.dkr.ecr.us-east-1.amazonaws.com/jkl-client:86b1fb8735c036fedf7d1e15dd6f669045c8e190"

snapshot     = "arn:aws:rds:us-east-2:12345:cluster-202301062012000004"
bucket_arn   = "arn:aws:s3:::foo-800000001"
test_website = "https://foo.com"

config = {
  JAVA_OPTS = "--add-opens -javaagent:/opt/foo/foo.jar"
  LOCATIONS = "classpath:flyway/migrations,classpath:flyway/foo/bar"
}