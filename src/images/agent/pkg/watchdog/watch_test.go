package watchdog

import (
	"fmt"
	"net"
	"testing"
	"time"
)

func TestA(t *testing.T) {
	fmt.Println(net.DialTimeout("tcp", "127.0.0.1:8000", 100*time.Millisecond))

	t.Fail()
}
