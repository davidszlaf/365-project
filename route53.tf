resource "aws_route53_zone" "main" {
  name = domain_name

  tags = {
    Environment = var.environment
  }
}

resource "aws_route53_record" "www" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "www.${domain_name}"
  type    = "CNAME"
  ttl     = "300"
  records = [aws_lb.main.dns_name]
}
