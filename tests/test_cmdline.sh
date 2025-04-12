#! /bin/bash

test_init() {
    true
    res=$?
    assertEquals "0" "$res"

    false
    res=$?
    assertEquals "1" "$res"
}

_test_fails() {
    true
    res=$?
    assertEquals "1" "$res"

    false
    res=$?
    assertEquals "0" "$res"
}


test_out1_1() {
    rm -f out1.txt
    echo -n "Test1" | ilff-cat -o out1.txt -
    echo -n "Test2" | ilff-cat -a -o out1.txt -
    echo -n "Test3" | ilff-cat -a -o out1.txt -
    echo -n "Test4" | ilff-cat -a -o out1.txt -
    test -f out1.txt
    assertEquals "$?" "0"

    sz=$(wc -c --total=only out1.txt)
    assertEquals "0" "$?"
    assertEquals "20" "$sz"

    nl=$(ilff-nlines out1.txt)
    assertEquals "0" "$?"
    assertEquals "4 out1.txt" "$nl"

    t1=$(ilff-getline out1.txt 0)
    assertEquals "0" "$?"
    t2=$(ilff-getline out1.txt 1)
    assertEquals "0" "$?"
    t3=$(ilff-getline out1.txt 2)
    assertEquals "0" "$?"
    t4=$(ilff-getline out1.txt 3)
    assertEquals "0" "$?"

    assertEquals "Test1" "$t1"
    assertEquals "Test2" "$t2"
    assertEquals "Test3" "$t3"
    assertEquals "Test4" "$t4"
}

test_out2_1() {
    rm -f out1.txt out2.txt
    echo -n "Test1" | ilff-tee out1.txt out2.txt

    t1=$(ilff-getline out1.txt 0)
    assertEquals "0" "$?"
    t2=$(ilff-getline out2.txt 0)
    assertEquals "0" "$?"

    assertEquals "Test1" "$t1"
    assertEquals "Test1" "$t2"
}

test_out2_2() {
    t1=$(ilff-getline out1.txt 1 2> log.err)
    assertNotEquals "0" "$?"
    grep -i "out of range" log.err > /dev/null
    assertEquals "0" "$?"

    t2=$(ilff-getline out2.txt 10 2> log.err)
    assertNotEquals "0" "$?"
    grep -i "out of range" log.err > /dev/null
    assertEquals "0" "$?"

    assertEquals "" "$t1"
    assertEquals "" "$t2"
}

test_cleanup() {
    ilff-rm out1.txt
    assertEquals "0" "$?"
    ilff-rm out2.txt
    assertEquals "0" "$?"

    rm -f log.err
}

. shunit2
