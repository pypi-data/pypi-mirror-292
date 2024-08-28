import scala.math.random
import org.apache.spark._
import com.amazonaws.AmazonServiceException
import com.amazonaws.auth.AWSCredentials
import com.amazonaws.auth.BasicAWSCredentials
import com.amazonaws.auth.AWSStaticCredentialsProvider
import com.amazonaws.client.builder.AwsClientBuilder
import com.amazonaws.services.s3.AmazonS3
import com.amazonaws.services.s3.AmazonS3ClientBuilder

object TestJobScala {
    def main(args: Array[String]) {

        val targetBucket = args(0);

        val credentials = new BasicAWSCredentials("test", "test");
        val region = System.getenv().get("AWS_REGION");
        val lsHost = System.getenv().get("LOCALSTACK_HOSTNAME");
        val edgePort = System.getenv().get("EDGE_PORT");
        val s3URL = String.format("http://%s:%s", lsHost, edgePort);
        val builder = AmazonS3ClientBuilder.standard().
            withEndpointConfiguration(
                new AwsClientBuilder.EndpointConfiguration(s3URL, region)).
            withCredentials(new AWSStaticCredentialsProvider(credentials));
        builder.setPathStyleAccessEnabled(true);
        val s3 = builder.build();
        s3.putObject(targetBucket, "job_done", "");

    }
}
