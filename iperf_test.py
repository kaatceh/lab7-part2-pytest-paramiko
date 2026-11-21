import parser


class TestSuite:
    def test_iperf3_client_connection(self, client):
        stdout, stderr = client
        assert stderr == ""

        intervals = parser.parser(stdout)
        assert len(intervals) > 0

        for item in intervals:
            assert item["Transfer"] > 2
            assert item["Bitrate"] > 20