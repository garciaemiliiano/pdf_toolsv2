const fs = require('fs-extra')
const FormData = require('form-data')
const _ = require('underscore')
function enviarPDF (requestParams, context, ee, next) {
  try {
    const formData = new FormData()

    formData.append('file', fs.createReadStream('files/test.pdf'))

    requestParams.body = formData
    return next()
  } catch (error) {
    console.log(error)
    throw error
  }
}

function enviarMergePDF (requestParams, context, ee, next) {
  try {
    const formData = new FormData()

    const fileNames = [
      'test1.pdf',
      'test.pdf',
      'test2.pdf',
      'test3.pdf',
      'test4.pdf',
      'test5.pdf'
    ] // Array de nombres de archivos PDF

    for (const fileName of fileNames) {
      const fileStream = fs.createReadStream(`files/${fileName}`)
      formData.append('files', fileStream)
    }
    requestParams.body = formData
    return next()
  } catch (error) {
    console.log(error)
    throw error
  }
}
module.exports = {
  enviarPDF,
  enviarMergePDF
}
