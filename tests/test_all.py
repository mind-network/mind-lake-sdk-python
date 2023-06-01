import test_base
import env
import test_create
import test_delete
import test_drop
import test_encryption
import test_insert
import test_link
import test_sharing
import test_update

def test_all(walletPrivateKeyAlice, walletPrivateKeyBob, walletAddressAlice, walletAddressBob, appKey):
    test_create.cases(walletPrivateKeyAlice, appKey)
    test_delete.cases(walletPrivateKeyAlice, appKey)
    test_drop.cases(walletPrivateKeyAlice, appKey)
    test_encryption.cases(walletPrivateKeyAlice, appKey)
    test_insert.cases(walletPrivateKeyAlice, appKey)
    test_link.cases(walletPrivateKeyAlice, walletPrivateKeyBob, walletAddressAlice, walletAddressBob, appKey)
    test_sharing.cases(walletPrivateKeyAlice, walletPrivateKeyBob, walletAddressAlice, walletAddressBob, appKey)
    test_update.cases(walletPrivateKeyAlice, appKey)

if __name__ == '__main__':
    test_all(env.walletPrivateKeyAlice, env.walletPrivateKeyBob, env.walletAddressAlice, env.walletAddressBob, env.appKey)