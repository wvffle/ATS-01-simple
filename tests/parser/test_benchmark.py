import time

from ats.parser.parser import parse


def benchmark(func):
    def wrapper():
        then = time.process_time()
        func()
        delta = time.process_time() - then
        assert delta < 0.1

    return wrapper


@benchmark
def test_micro_program():
    parse(
        """
            procedure proc {
                test = 8;
            }
        """
    )


@benchmark
def test_small_program():
    parse(
        """
            procedure test {
                a = 8;
                while a {
                    a = a + 1;
                }
                if b then {
                    a = a + 2;
                }
                else {
                    a = a + b + s + 5 + a + b+ 3 + 4 +5 +f +6 +d+ s;
                }
            }

        """
    )


@benchmark
def test_medium_program():
    parse(
        """
            procedure test {
                a = 8;
                while a {
                    if b then {
                        a = a + 2;
                    } else {
                        if b then {
                            a = a + 2;
                        } else {
                            a = a + b + s + 5 + a + b+ 3 + 4 +5 +f +6 +d+ s;
                        }
                    }
                }

                if b then {
                    if b then {
                        a = a + 2;
                    } else {
                        if b then {
                            a = a + 2;
                        } else {
                            a = a + b + s + 5 + a + b+ 3 + 4 +5 +f +6 +d+ s;
                        }
                    }
                } else {
                    if b then {
                        a = a + 2;
                    } else {
                        a = a + b + s + 5 + a + b+ 3 + 4 +5 +f +6 +d+ s;
                    }
                }
            }

        """
    )


@benchmark
def test_big_program():
    parse(
        """
            procedure test {
                a = 8;
                while a {
                    if b then {
                        a = a + 2;
                    } else {
                        if b then {
                            a = a + 2;
                        } else {
                if b then {
                    if b then {
                while a {
                    if b then {
                        a = a + 2;
                    } else {
                        if b then {
                if b then {
                    if b then {
                while a {
                    if b then {
                while a {
                    if b then {
                        a = a + 2;
                    } else {
                        if b then {
                            a = a + 2;
                        } else {
                if b then {
                    if b then {
                while a {
                    if b then {
                        a = a + 2;
                    } else {
                        if b then {
                if b then {
                    if b then {
                while a {
                    if b then {
                        a = a + 2;
                    } else {
                        if b then {
                            a = a + 2;
                        } else {
                            a = a + b + s + 5 + a + b+ 3 + 4 +5 +f +6 +d+ s;
                        }
                    }
                }
                    } else {
                        if b then {
                            a = a + 2;
                        } else {
                            a = a + b + s + 5 + a + b+ 3 + 4 +5 +f +6 +d+ s;
                        }
                    }
                } else {
                    if b then {
                        a = a + 2;
                    } else {
                        a = a + b + s + 5 + a + b+ 3 + 4 +5 +f +6 +d+ s;
                    }
                }
                        } else {
                            a = a + b + s + 5 + a + b+ 3 + 4 +5 +f +6 +d+ s;
                        }
                    }
                }
                    } else {
                        if b then {
                            a = a + 2;
                        } else {
                            a = a + b + s + 5 + a + b+ 3 + 4 +5 +f +6 +d+ s;
                        }
                    }
                } else {
                    if b then {
                        a = a + 2;
                    } else {
                        a = a + b + s + 5 + a + b+ 3 + 4 +5 +f +6 +d+ s;
                    }
                }
                        }
                    }
                }

                if b then {
                    if b then {
                while a {
                    if b then {
                        a = a + 2;
                    } else {
                        if b then {
                if b then {
                    if b then {
                while a {
                    if b then {
                        a = a + 2;
                    } else {
                        if b then {
                            a = a + 2;
                        } else {
                            a = a + b + s + 5 + a + b+ 3 + 4 +5 +f +6 +d+ s;
                        }
                    }
                }
                    } else {
                        if b then {
                            a = a + 2;
                        } else {
                            a = a + b + s + 5 + a + b+ 3 + 4 +5 +f +6 +d+ s;
                        }
                    }
                } else {
                    if b then {
                        a = a + 2;
                    } else {
                        a = a + b + s + 5 + a + b+ 3 + 4 +5 +f +6 +d+ s;
                    }
                }
                        } else {
                            a = a + b + s + 5 + a + b+ 3 + 4 +5 +f +6 +d+ s;
                        }
                    }
                }
                    } else {
                        if b then {
                            a = a + 2;
                        } else {
                            a = a + b + s + 5 + a + b+ 3 + 4 +5 +f +6 +d+ s;
                        }
                    }
                } else {
                    if b then {
                        a = a + 2;
                    } else {
                        a = a + b + s + 5 + a + b+ 3 + 4 +5 +f +6 +d+ s;
                    }
                }
                    } else {
                        if b then {
                            a = a + 2;
                        } else {
                            a = a + b + s + 5 + a + b+ 3 + 4 +5 +f +6 +d+ s;
                        }
                    }
                }
                    } else {
                        if b then {
                            a = a + 2;
                        } else {
                            a = a + b + s + 5 + a + b+ 3 + 4 +5 +f +6 +d+ s;
                        }
                    }
                } else {
                    if b then {
                        a = a + 2;
                    } else {
                        a = a + b + s + 5 + a + b+ 3 + 4 +5 +f +6 +d+ s;
                    }
                }
                        } else {
                            a = a + b + s + 5 + a + b+ 3 + 4 +5 +f +6 +d+ s;
                        }
                    }
                }
                    } else {
                        if b then {
                            a = a + 2;
                        } else {
                            a = a + b + s + 5 + a + b+ 3 + 4 +5 +f +6 +d+ s;
                        }
                    }
                } else {
                    if b then {
                        a = a + 2;
                    } else {
                        a = a + b + s + 5 + a + b+ 3 + 4 +5 +f +6 +d+ s;
                    }
                }
                        }
                    }
                }

                if b then {
                    if b then {
                while a {
                    if b then {
                        a = a + 2;
                    } else {
                        if b then {
                if b then {
                    if b then {
                while a {
                    if b then {
                        a = a + 2;
                    } else {
                        if b then {
                            a = a + 2;
                        } else {
                            a = a + b + s + 5 + a + b+ 3 + 4 +5 +f +6 +d+ s;
                        }
                    }
                }
                    } else {
                        if b then {
                            a = a + 2;
                        } else {
                            a = a + b + s + 5 + a + b+ 3 + 4 +5 +f +6 +d+ s;
                        }
                    }
                } else {
                    if b then {
                        a = a + 2;
                    } else {
                        a = a + b + s + 5 + a + b+ 3 + 4 +5 +f +6 +d+ s;
                    }
                }
                        } else {
                            a = a + b + s + 5 + a + b+ 3 + 4 +5 +f +6 +d+ s;
                        }
                    }
                }
                    } else {
                        if b then {
                            a = a + 2;
                        } else {
                            a = a + b + s + 5 + a + b+ 3 + 4 +5 +f +6 +d+ s;
                        }
                    }
                } else {
                    if b then {
                        a = a + 2;
                    } else {
                        a = a + b + s + 5 + a + b+ 3 + 4 +5 +f +6 +d+ s;
                    }
                }
            }
        """
    )
