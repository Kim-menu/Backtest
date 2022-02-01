import BackTester


# my_back_tester = BackTester.SmurfTester(0)
# my_back_tester = BackTester.SimpleTester(0)
my_back_tester = BackTester.RebalancingTester(0)

# TQQQ experiment
my_back_tester.simulation('TQQQ', '2021-01-01', '2021-12-31', 800)

# SAMSUNG experiment
# my_back_tester.simulation('005935', '2021-01-01', '2021-12-31', 500000)
