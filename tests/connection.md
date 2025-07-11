Failure scenarios for rabbitmq connection to test:

kill the rabbitmq server during operation
block traffic on rabbitmq port with iptables
delete queue or exchange on rabbitmq
publish on non-existent exchange
double acknowledge (basic_ack)
configure low hearbeat value and simulate slow processing (by putting sleep in callback)

