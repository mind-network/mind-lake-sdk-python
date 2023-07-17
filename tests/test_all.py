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

def test_all(walletPrivateKeyAlice, walletPrivateKeyBob, walletAddressAlice, walletAddressBob, appKey, GATEWAY):
    test_create.cases(walletPrivateKeyAlice, appKey, GATEWAY)
    test_delete.cases(walletPrivateKeyAlice, appKey, GATEWAY)
    test_drop.cases(walletPrivateKeyAlice, appKey, GATEWAY)
    test_encryption.cases(walletPrivateKeyAlice, appKey, GATEWAY)
    test_insert.cases(walletPrivateKeyAlice, appKey, GATEWAY)
    test_link.cases(walletPrivateKeyAlice, walletPrivateKeyBob, walletAddressAlice, walletAddressBob, appKey, GATEWAY)
    test_sharing.cases(walletPrivateKeyAlice, walletPrivateKeyBob, walletAddressAlice, walletAddressBob, appKey, GATEWAY)
    test_update.cases(walletPrivateKeyAlice, appKey, GATEWAY)

if __name__ == '__main__':
    if hasattr(env, 'GATEWAY') and env.GATEWAY:
        test_all(env.walletPrivateKeyAlice, env.walletPrivateKeyBob, env.walletAddressAlice, env.walletAddressBob, env.appKey, env.GATEWAY)
    else:
        test_all(env.walletPrivateKeyAlice, env.walletPrivateKeyBob, env.walletAddressAlice, env.walletAddressBob, env.appKey, None)
